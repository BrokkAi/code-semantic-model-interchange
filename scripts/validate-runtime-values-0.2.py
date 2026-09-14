#!/usr/bin/env python3
"""Check portable runtime contracts and a bounded, fail-closed wire consumer.

This validates evidence consistency, not reviewer authority or runtime truth.
The consumer requires an independently supplied policy digest for activation.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/runtime-values/0.2"
VOCABULARY = "csmi.runtime-values"
VERSION = "0.2.0"
SCHEMA = "https://csmi.brokk.ai/schema/profiles/runtime-values/0.2/schema.json"
FAMILIES = {
    "runtime-contracts": ("runtime-contract", "contractId"),
    "runtime-targets": ("runtime-target", "targetId"),
    "runtime-activations": ("runtime-activation", "activationId"),
    "runtime-bindings": ("runtime-binding", "bindingId"),
    "runtime-observations": ("runtime-observation", "observationId"),
}
CONTEXT = "https://csmi.brokk.ai/runtime-context/"
EQUALITY = "https://csmi.brokk.ai/key-equality/"
DIMENSIONS = ("platform", "architecture", "realm", "moduleMode", "launchMode", "initializationBoundary")
CONTEXTS = {
    CONTEXT + "node": {
        "platform": {"linux", "darwin", "windows"},
        "architecture": {"x64", "arm64"},
        "realm": {"main", "worker-copy", "worker-shared"},
        "moduleMode": {"commonjs", "esm"},
        "launchMode": {"script", "eval", "stdin", "repl", "worker"},
        "initializationBoundary": {"runtime-entry", "application-entry"},
    },
    CONTEXT + "cpython": {
        "platform": {"linux", "darwin", "windows"},
        "architecture": {"x64", "arm64"},
        "realm": {"main", "subinterpreter"},
        "moduleMode": {"python"},
        "launchMode": {"script", "module", "command", "stdin", "repl"},
        "initializationBoundary": {"module-import", "application-entry"},
    },
}
PACKAGE_SCHEMES = {
    "pkg:generic/nodejs.org/node": "semver",
    "pkg:generic/python.org/cpython": "pypi",
}


def load(path: Path) -> Any:
    def unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON member {key}")
            result[key] = value
        return result
    return json.loads(path.read_text(), object_pairs_hook=unique)


def canonical(value: Any) -> bytes:
    """JCS for this schema's integer-only JSON; normalize all profile arrays as sets."""
    def render(item: Any) -> str:
        if isinstance(item, dict):
            keys = sorted(item, key=lambda key: key.encode("utf-16-be"))
            return "{" + ",".join(render(key) + ":" + render(item[key]) for key in keys) + "}"
        if isinstance(item, list):
            entries = sorted({render(child).encode("utf-8") for child in item})
            return "[" + ",".join(child.decode("utf-8") for child in entries) + "]"
        if isinstance(item, str):
            item.encode("utf-8")  # Reject lone surrogates, as I-JSON requires.
        elif isinstance(item, int) and not isinstance(item, bool):
            if abs(item) > 9007199254740991:
                raise ValueError("integer exceeds I-JSON exact range")
        elif item is not None and not isinstance(item, bool):
            raise ValueError("profile canonicalization supports only exact integers")
        return json.dumps(item, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    return render(value).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value)).hexdigest()


def package(selector: dict) -> tuple[str, str | None]:
    purl = selector["purl"]
    # Qualified/other registered PURLs remain valid opaque identities here.
    base, marker, version = purl.partition("@")
    return base, version if marker else None


def selector_issues(selector: dict) -> list[str]:
    issues = []
    purl = selector["purl"]
    if "#" in purl or re.search(r"\s", purl) or not re.fullmatch(r"pkg:[a-z][a-z0-9.+-]*/[^\s]+", purl):
        issues.append("invalid PURL or forbidden subpath")
    if re.search(r"%(?![0-9A-F]{2})", purl):
        issues.append("noncanonical PURL percent encoding")
    coordinate = purl[4:].split("?", 1)[0].split("@", 1)[0]
    if "//" in coordinate or coordinate.endswith("/") or any(part in {".", ".."} for part in coordinate.split("/")):
        issues.append("invalid PURL path component")
    for value in selector.get("digests", []):
        expected = {"sha-256": 64, "sha-384": 96, "sha-512": 128}[value["algorithm"]]
        if len(value["value"]) != expected:
            issues.append("artifact digest length disagrees with algorithm")
        if value["coverage"] in {"source-tree", "directory-tree"} and "canonicalization" not in value:
            issues.append("tree artifact digest requires canonicalization")
        if value["coverage"] in {"contract-content", "profile-content", "target-evidence", "activation-snapshot"}:
            issues.append("semantic/evidence digest is not artifact-byte coverage")
    version_range = selector.get("versionRange")
    numeric = r"(?:0|[1-9][0-9]*)"
    prerelease = rf"(?:{numeric}|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    semver = rf"{numeric}\.{numeric}\.{numeric}(?:-{prerelease}(?:\.{prerelease})*)?(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?"
    base, exact = package(selector)
    if base == "pkg:generic/nodejs.org/node" and exact is not None and not re.fullmatch(semver, exact):
        issues.append("invalid canonical Node release version")
    if version_range is not None:
        if not re.fullmatch(r"vers:[a-z][a-z0-9.-]*/[^\s]+", version_range):
            issues.append("malformed VERS")
        else:
            constraints = version_range.split("/", 1)[1].split("|")
            if any(not part for part in constraints) or ("*" in constraints and len(constraints) != 1):
                issues.append("malformed VERS constraints")
            versions = [re.sub(r"^(?:>=|<=|!=|>|<|=)", "", part) for part in constraints]
            if version_range.startswith("vers:semver/") and constraints != ["*"]:
                if any(not re.fullmatch(semver, version) for version in versions):
                    issues.append("invalid SemVer boundary")
            if len(set(versions)) != len(versions):
                issues.append("duplicate VERS version boundary")
            if all(re.fullmatch(r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)", v) for v in versions):
                numbers = [tuple(map(int, v.split("."))) for v in versions]
                if numbers != sorted(numbers):
                    issues.append("noncanonical reversed VERS boundaries")
                directions = [part[0] for part in constraints if part[0] in "<>"]
                if any(a == b for a, b in zip(directions, directions[1:])):
                    issues.append("invalid VERS interval alternation")
    return issues


def interval(selector: dict) -> tuple | None:
    """Bounded stable release intervals. None means supported structure, unsupported comparison."""
    base, exact = package(selector)
    expected = PACKAGE_SCHEMES.get(base)
    if expected is None:
        return None
    stable = r"(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
    def number(value: str) -> tuple[int, ...]:
        return tuple(map(int, value.split(".")))
    if exact is not None:
        return (number(exact), True, number(exact), True) if re.fullmatch(stable, exact) else None
    value = selector["versionRange"]
    if not value.startswith(f"vers:{expected}/"):
        return None
    body = value.split("/", 1)[1]
    if re.fullmatch(stable, body):
        return number(body), True, number(body), True
    match = re.fullmatch(f"(>=|>)({stable})\\|(<|<=)({stable})", body)
    if match:
        return number(match[2]), match[1] == ">=", number(match[4]), match[3] == "<="
    return None


def interval_relation(contract: tuple, target: tuple) -> str:
    lo, li, hi, hi_i = contract
    tlo, tli, thi, thi_i = target
    if hi < tlo or (hi == tlo and not (hi_i and tli)) or thi < lo or (thi == lo and not (thi_i and li)):
        return "not-matched"
    lower = lo < tlo or (lo == tlo and (li or not tli))
    upper = hi > thi or (hi == thi and (hi_i or not thi_i))
    return "matched" if lower and upper else "indeterminate"


def artifact_match(required: list[dict], actual: list[dict]) -> str:
    missing = False
    groups: dict[tuple, list[dict]] = {}
    for item in required:
        groups.setdefault((item["coverage"], item.get("canonicalization")), []).append(item)
    for (coverage, canon), alternatives in groups.items():
        comparable = [(wanted, found) for wanted in alternatives for found in actual
                      if found["coverage"] == coverage and found.get("canonicalization") == canon
                      and found["algorithm"] == wanted["algorithm"]]
        if any(a["value"] != b["value"] for a, b in comparable):
            return "not-matched"
        if not comparable:
            missing = True
    return "indeterminate" if missing else "matched"


def selector_match(required: dict, actual: dict | None) -> str:
    if actual is None:
        return "indeterminate"
    rb, _ = package(required)
    ab, _ = package(actual)
    if rb not in PACKAGE_SCHEMES or ab not in PACKAGE_SCHEMES:
        return "unsupported"
    if rb != ab:
        return "not-matched"
    r, a = interval(required), interval(actual)
    version = interval_relation(r, a) if r is not None and a is not None else "unsupported"
    artifacts = artifact_match(required.get("digests", []), actual.get("digests", []))
    return conjunct([version, artifacts])


def conjunct(results: list[str]) -> str:
    for outcome in ("not-matched", "unsupported", "indeterminate"):
        if outcome in results:
            return outcome
    return "matched"


def applicable(contract: dict, target: dict) -> str:
    definition, context = contract["definition"], target["definition"]["context"]
    target_definition = target["definition"]
    constraints = definition["context"]
    selectors = [selector_match(selector, target_definition.get("runtime")) for selector in definition["applicability"]["selectors"]]
    selection = "matched" if "matched" in selectors else "unsupported" if "unsupported" in selectors else "indeterminate" if "indeterminate" in selectors else "not-matched"
    results = [selection]
    equality = definition["behavior"]["keyEquality"]
    if equality["version"] != VERSION or equality["identifier"] not in {EQUALITY + "exact-string", EQUALITY + "exact-index", EQUALITY + "platform-defined"}:
        results.append("unsupported")
    scheme = constraints["scheme"]
    if scheme["identifier"] not in CONTEXTS or scheme["version"] != VERSION:
        results.append("unsupported")
    elif context["scheme"] != scheme:
        results.append("not-matched" if context["scheme"]["identifier"] in CONTEXTS and context["scheme"]["version"] == VERSION else "unsupported")
    else:
        for field in DIMENSIONS:
            if context[field] == "unknown":
                results.append("indeterminate")
            elif context[field] not in constraints[field]:
                results.append("not-matched")
        if not set(definition["assumptions"]).issubset(target_definition["assumptions"]):
            results.append("indeterminate")
    if target_definition["basis"] == "unknown" or target_definition["coverage"]["status"] != "complete":
        results.append("indeterminate")
    return conjunct(results)


def activation_input(activation: dict, contracts: dict[str, dict], targets: dict[str, dict]) -> dict:
    return {
        "targetDigest": targets[activation["targetId"]]["targetDigest"],
        "surface": activation["surface"],
        "contracts": [contracts[name] for name in activation["candidateIds"]],
        **{name: activation[name] for name in ("candidateCoverage", "disabledIds", "reviews", "policy", "outcome", "selectedIds")},
    }


def evaluate_activation(activation: dict, contracts: dict[str, dict], targets: dict[str, dict], accepted_policy_digest: str | None = None) -> tuple[str, list[str]]:
    """Interpret with independent consumer policy approval; never trust an embedded reviewer list by default."""
    target = targets[activation["targetId"]]
    if activation["candidateCoverage"]["status"] != "complete":
        return "indeterminate", []
    candidates = [contracts[name] for name in activation["candidateIds"] if name not in activation["disabledIds"]]
    if not candidates:
        return ("disabled" if activation["candidateIds"] else "not-matched"), []
    statuses = {item["contractId"]: applicable(item, target) for item in candidates}
    possible = [item for item in candidates if statuses[item["contractId"]] != "not-matched"]
    if not possible:
        return "not-matched", []
    # A content conflict cannot be hidden behind incomplete evidence or preference order.
    definitions: dict[tuple[str, str], set[bytes]] = {}
    for item in possible:
        definition = item["definition"]
        definitions.setdefault((definition["identifier"], definition["version"]), set()).add(canonical(definition))
    if any(len(values) > 1 for values in definitions.values()):
        return "conflict", []
    signatures = {canonical({key: item["definition"][key] for key in ("surface", "languages", "assumptions", "behavior")}) for item in possible}
    if len(signatures) > 1:
        return "conflict", []
    if "unsupported" in statuses.values():
        return "unsupported", []
    if "indeterminate" in statuses.values():
        return "indeterminate", []
    policy = activation["policy"]
    if accepted_policy_digest != digest(policy):
        return "review-required", []
    for item in possible:
        reviews = [review for review in activation["reviews"] if review["contractDigest"] == item["contractDigest"]
                   and review["targetDigest"] == target["targetDigest"] and review["purpose"] == policy["purpose"]
                   and review["reviewer"] in policy["trustedReviewers"]]
        if not reviews or any(review["decision"] != "approved" for review in reviews):
            return "review-required", []
    return "matched", sorted(item["contractId"] for item in possible)


def key_relation(left: dict, right: dict, scheme: dict) -> str:
    if left["kind"] in {"dynamic", "unsupported"} or right["kind"] in {"dynamic", "unsupported"}:
        return "unknown"
    if scheme["version"] != VERSION:
        return "unknown"
    expected = {EQUALITY + "exact-string": "property", EQUALITY + "exact-index": "index"}.get(scheme["identifier"])
    if left["kind"] != expected or right["kind"] != expected:
        return "unknown"
    return "equal" if left["value"] == right["value"] else "different"


def identity_relation(left: dict, right: dict, supported_schemes: set[tuple[str, str]]) -> str:
    """Identity schemes require explicit consumer support, never inference from hash equality."""
    scheme = left["scheme"]
    if scheme != right["scheme"] or (scheme["identifier"], scheme["version"]) not in supported_schemes:
        return "unknown"
    return "equal" if left == right else "unknown"


def store_relation(left: dict, right: dict, supported_schemes: set[tuple[str, str]] | None = None) -> str:
    """Opaque identity inequality is not a non-aliasing proof."""
    if left["relationship"] == "unknown" or right["relationship"] == "unknown":
        return "unknown"
    supported = supported_schemes or set()
    if identity_relation(left["invocation"], right["invocation"], supported) != "equal":
        return "unknown"
    if identity_relation(left["backing"], right["backing"], supported) == "equal":
        if identity_relation(left["realm"], right["realm"], supported) == "equal" or left["relationship"] == right["relationship"] == "shared":
            return "equal"
    return "unknown"


def reference_checks(document: dict) -> list[str]:
    """Adversarial consumer cases independent of fixture outcome generation."""
    errors = []
    model = document["semanticModels"][0]
    records = {family: [fact["payload"] for fact in model["extensionFacts"] if fact["family"] == family] for family in FAMILIES}
    contract = records["runtime-contracts"][0]
    target = records["runtime-targets"][0]
    activation = records["runtime-activations"][0]
    contracts = {item["contractId"]: item for item in records["runtime-contracts"]}
    targets = {item["targetId"]: item for item in records["runtime-targets"]}
    def expect(name: str, actual: Any, expected: Any) -> None:
        if actual != expected:
            errors.append(f"{name}: expected {expected!r}, got {actual!r}")
    runtime = target["definition"]["runtime"]
    base = {"purl": "pkg:generic/nodejs.org/node", "versionRange": "vers:semver/>=22.11.0|<23.0.0"}
    for version, expected in (("22.11.0", "matched"), ("22.99.0", "matched"), ("23.0.0", "not-matched"), ("22.10.9", "not-matched"), ("22.11.0-rc.1", "unsupported")):
        expect("version " + version, selector_match(base, {"purl": "pkg:generic/nodejs.org/node@" + version}), expected)
    expect("contained range", selector_match(base, {**base, "versionRange": "vers:semver/>=22.12.0|<22.13.0"}), "matched")
    expect("overlapping range", selector_match(base, {**base, "versionRange": "vers:semver/>=22.12.0|<24.0.0"}), "indeterminate")
    expect("excluded version range unsupported", selector_match({**base, "versionRange": "vers:semver/>=22.11.0|!=22.12.0|<23.0.0"}, runtime), "unsupported")
    expect("malformed interval", bool(selector_issues({**base, "versionRange": "vers:semver/>=23.0.0|<22.0.0"})), True)
    for boundary in ("bogus", "23", "22.11", "023.0.0", "23.0.0-01"):
        expect("malformed version " + boundary, bool(selector_issues({**base, "versionRange": "vers:semver/>=22.11.0|<" + boundary})), True)
    actual_bytes = {"algorithm": "sha-256", "coverage": "synthetic-archive", "value": "1" * 64}
    specialized = {"purl": runtime["purl"], "digests": [actual_bytes]}
    expect("specialization missing bytes", selector_match(specialized, runtime), "indeterminate")
    expect("specialization matching bytes", selector_match(specialized, specialized), "matched")
    expect("specialization wrong coverage", selector_match(specialized, {**specialized, "digests": [{**actual_bytes, "coverage": "other"}]}), "indeterminate")
    expect("specialization wrong bytes", selector_match(specialized, {**specialized, "digests": [{**actual_bytes, "value": "2" * 64}]}), "not-matched")
    approved = digest(activation["policy"])
    expect("external policy absent", evaluate_activation(activation, contracts, targets)[0], "review-required")
    for field, value in (("reviews", []), ("reviews", [{**activation["reviews"][0], "targetDigest": "f" * 64}]), ("candidateCoverage", {"status": "partial", "limitations": ["inventory-incomplete"]})):
        candidate = {**activation, field: value}
        expect("activation " + field, evaluate_activation(candidate, contracts, targets, approved)[0], "indeterminate" if field == "candidateCoverage" else "review-required")
    expect("explicit disable", evaluate_activation({**activation, "disabledIds": activation["candidateIds"]}, contracts, targets, approved)[0], "disabled")
    for candidate_ids, disabled_ids in (([], []), (activation["candidateIds"], activation["candidateIds"])):
        incomplete = {**activation, "candidateIds": candidate_ids, "disabledIds": disabled_ids,
                      "candidateCoverage": {"status": "partial", "limitations": ["inventory-incomplete"]}}
        expect("incomplete empty or disabled inventory", evaluate_activation(incomplete, contracts, targets, approved)[0], "indeterminate")
    duplicate = copy.deepcopy(contract)
    duplicate["contractId"] = "equivalent"
    duplicate["definition"]["identifier"] += "/equivalent"
    duplicate["contractDigest"] = digest(duplicate["definition"])
    all_contracts = {**contracts, "equivalent": duplicate}
    both = {**activation, "candidateIds": [*activation["candidateIds"], "equivalent"], "reviews": [*activation["reviews"], {**activation["reviews"][0], "contractDigest": duplicate["contractDigest"]}]}
    expect("equivalent candidates", evaluate_activation(both, all_contracts, targets, approved)[0], "matched")
    duplicate["definition"]["behavior"]["absent"] = "exception"
    expect("conflicting candidate", evaluate_activation(both, all_contracts, targets, approved)[0], "conflict")
    string_scheme = {"identifier": EQUALITY + "exact-string", "version": VERSION}
    left, right = {"kind": "property", "value": "Config"}, {"kind": "property", "value": "CONFIG"}
    expect("exact strings", key_relation(left, right, string_scheme), "different")
    expect("platform equality unknown", key_relation(left, right, {**string_scheme, "identifier": EQUALITY + "platform-defined"}), "unknown")
    store = records["runtime-observations"][0]["store"]
    stale = copy.deepcopy(records["runtime-observations"][0])
    stale["proof"]["closureDigest"] = "f" * 64
    expect("stale proof digest", "proof closure digest mismatch" in payload_issues(stale), True)
    supported = {(store["backing"]["scheme"]["identifier"], store["backing"]["scheme"]["version"])}
    expect("unsupported identity scheme", store_relation(store, store), "unknown")
    expect("same supported store", store_relation(store, store, supported), "equal")
    expect("opaque stores not disjoint", store_relation(store, {**store, "backing": {**store["backing"], "locatorDigest": "f" * 64}}, supported), "unknown")
    different_scheme = {**store["backing"], "scheme": {**store["backing"]["scheme"], "version": "unsupported"}}
    expect("identical digest different scheme", identity_relation(store["backing"], different_scheme, supported), "unknown")
    for field in ("context", "behavior", "assumptions"):
        changed = copy.deepcopy(contract["definition"])
        if field == "context":
            changed[field]["platform"] = ["windows"]
        elif field == "behavior":
            changed[field]["read"]["exceptions"] = "unknown"
        else:
            changed[field].append("https://example.test/another-assumption")
        expect("contract cache change " + field, digest(changed) != contract["contractDigest"], True)
    for field, value in (("policy", {**activation["policy"], "inputsDigest": "f" * 64}), ("reviews", []), ("disabledIds", activation["candidateIds"])):
        changed = {**activation, field: value}
        expect("activation cache change " + field, digest(activation_input(changed, contracts, targets)) != activation["activationDigest"], True)
    return errors


def payload_issues(payload: dict) -> list[str]:
    issues = []
    kind = payload["kind"]
    if kind == "runtime-contract":
        definition = payload["definition"]
        if payload["contractDigest"] != digest(definition):
            issues.append("contract digest mismatch")
        for selector in definition["applicability"]["selectors"]:
            issues.extend(selector_issues(selector))
            if definition["applicability"]["basis"] == "artifact-specific" and "versionRange" in selector:
                issues.append("artifact-specific specialization requires an exact artifact version")
        context = definition["context"]
        supported = CONTEXTS.get(context["scheme"]["identifier"])
        if supported and context["scheme"]["version"] == VERSION:
            for field in DIMENSIONS:
                if not set(context[field]).issubset(supported[field]):
                    issues.append(f"invalid known context constraint {field}")
        behavior = definition["behavior"]
        if behavior["coverage"]["status"] == "complete" and (
                behavior["read"]["exceptions"] == "unknown" or behavior["read"]["materialization"] == "unknown"
                or "unknown" in behavior["write"].values() or "unknown" in behavior["delete"].values()
                or any(origin["origin"] == "unknown" for origin in behavior["initialOrigins"])):
            issues.append("complete behavior contains unknown semantics")
        equality = behavior["keyEquality"]
        if equality["version"] == VERSION:
            if equality["identifier"] == EQUALITY + "exact-string" and behavior["keyDomain"] != "static-property":
                issues.append("string equality requires property keys")
            if equality["identifier"] == EQUALITY + "exact-index" and behavior["keyDomain"] != "static-index":
                issues.append("index equality requires index keys")
        if context["scheme"] == {"identifier": CONTEXT + "node", "version": VERSION}:
            if definition["surface"]["container"] == "env" and "windows" in context["platform"] and set(context["realm"]) & {"main", "worker-shared"}:
                if equality["identifier"] == EQUALITY + "exact-string":
                    issues.append("Windows native environment cannot use exact-string equality")
            if definition["surface"]["container"] == "argv" and set(context["launchMode"]) != {"script"}:
                if any(origin["origin"] in {"application-argument", "entry-path"} for origin in behavior["initialOrigins"]):
                    issues.append("script argv origins cannot cover another launch mode")
            if definition["surface"]["container"] == "argv" and behavior["write"]["conversion"] == "string-conversion":
                issues.append("ordinary argv writes do not imply string conversion")
        if context["scheme"] == {"identifier": CONTEXT + "cpython", "version": VERSION} and definition["surface"]["container"] == "environ":
            if behavior["lookup"] != "mapping-entry" or behavior["absent"] != "exception":
                issues.append("CPython environ subscription requires mapping/missing-key exception behavior")
            if behavior["write"]["conversion"] == "string-conversion":
                issues.append("CPython environ assignments do not imply arbitrary string conversion")
        ranges = []
        for origin in behavior["initialOrigins"]:
            keys = origin["keys"]
            if (keys["kind"] == "all-properties") != (behavior["keyDomain"] == "static-property"):
                issues.append("origin key domain mismatch")
            if keys["kind"] == "index-range":
                if keys["minimum"] > keys["maximum"]:
                    issues.append("reversed origin key range")
                ranges.append((keys["minimum"], keys["maximum"]))
        ranges.sort()
        if any(a[1] >= b[0] for a, b in zip(ranges, ranges[1:])):
            issues.append("overlapping origin key ranges")
    elif kind == "runtime-target":
        definition = payload["definition"]
        if payload["targetDigest"] != digest(definition):
            issues.append("target digest mismatch")
        if "runtime" in definition:
            issues.extend(selector_issues(definition["runtime"]))
        resources = definition["resources"]
        if len({item["resource"] for item in resources}) != len(resources):
            issues.append("conflicting resource identities in partition")
        if definition["basis"] == "unknown" and definition["coverage"]["status"] == "complete":
            issues.append("unknown target cannot have complete target coverage")
        context = definition["context"]
        supported = CONTEXTS.get(context["scheme"]["identifier"])
        if supported and context["scheme"]["version"] == VERSION:
            for field in DIMENSIONS:
                if context[field] != "unknown" and context[field] not in supported[field]:
                    issues.append(f"invalid known target context {field}")
        if definition["basis"] == "deployment-observation" and ("runtime" not in definition or "versionRange" in definition["runtime"]):
            issues.append("deployment observation requires an exact observed runtime")
    elif kind in {"runtime-binding", "runtime-observation"}:
        source = payload["source"]
        if source["endByte"] <= source["startByte"]:
            issues.append("empty source range")
        expected = {"scope": "scope", "root": "value", "container": "value"} if kind == "runtime-binding" else {"baseValue": "value", "loadOperation": "operation", "resultValue": "value", "point": "point"}
        for field, expected_kind in expected.items():
            identity = payload[field]
            if identity["kind"] != expected_kind or identity["ownerDigest"] != source["resourceDigest"]:
                issues.append(f"{field} kind/source owner mismatch")
        if kind == "runtime-binding":
            if payload["outcome"] == "exact" and (payload["lexicalBinding"] != "absent" or payload["rebinding"] != "excluded"):
                issues.append("exact binding requires excluded lexical/rebinding alternatives")
            if payload["outcome"] == "excluded" and payload["lexicalBinding"] != "present" and payload["rebinding"] != "present":
                issues.append("excluded binding lacks conclusive exclusion")
            if payload["coverage"]["status"] == "complete" and payload["outcome"] not in {"exact", "excluded"}:
                issues.append("complete binding is unresolved")
        else:
            proof = payload["proof"]
            if proof["closureDigest"] != digest({name: value for name, value in proof.items() if name != "closureDigest"}):
                issues.append("proof closure digest mismatch")
            key = payload["key"]
            storage_key = payload.get("storageKey")
            if proof["keyNormalization"] == "exact":
                if key["kind"] not in {"property", "index"} or not storage_key or storage_key["kind"] not in {"property", "index"}:
                    issues.append("exact storage key normalization requires static source and storage keys")
            elif storage_key is not None:
                issues.append("unknown key normalization cannot publish an exact storage key")
            if proof["normal"] == "exact" and payload["phase"] != "after-effects":
                issues.append("exact normal observation must follow effects")
            if payload["origin"] == "initial-if-present" and (proof["mutation"] != "pristine" or proof["initialization"] != "closed" or proof["dependencies"] != "closed"):
                issues.append("initial origin requires pristine mutation evidence")
            if payload["origin"] in {"written", "deleted"} and proof["mutation"] != payload["origin"]:
                issues.append("origin and mutation evidence disagree")
            if payload["sourceForm"] == "dot" and key["kind"] != "property":
                issues.append("dot form requires property key")
            if payload["sourceForm"] == "bracket-number" and key["kind"] != "index":
                issues.append("number form requires index key")
            if payload["sourceForm"] == "bracket-string" and key["kind"] != "property":
                issues.append("string form requires property key")
            if payload["coverage"]["status"] == "complete":
                if (proof["initialization"] != "closed" or proof["dependencies"] != "closed"
                        or proof["mutation"] == "unknown" or proof["lookup"] in {"inherited", "accessor", "proxy", "unknown"}
                        or proof["materialization"] != "resolved" or proof["normal"] != "exact" or proof["exceptional"] == "unknown"
                        or key["kind"] not in {"property", "index"} or payload["origin"] == "unknown"
                        or proof["keyNormalization"] != "exact"
                        or payload["store"]["relationship"] == "unknown"):
                    issues.append("complete observation has open proof obligations")
    return issues


def document_issues(document: dict) -> list[str]:
    core = Draft202012Validator(load(ROOT / "spec/0.1/schema.json"), format_checker=FormatChecker())
    validator = Draft202012Validator(load(PROFILE / "schema.json"), format_checker=FormatChecker())
    if not core.is_valid(document) or document.get("documentType") != "semantic-document":
        return ["invalid core structure"]
    issues = []
    provenance = {entry["id"] for entry in document["provenanceRecords"]}
    if len(provenance) != len(document["provenanceRecords"]):
        issues.append("duplicate provenance identity")
    for model in document["semanticModels"]:
        uses = [use for use in model.get("vocabularyUses", []) if use["identifier"] == VOCABULARY]
        if not uses and not any(fact["vocabulary"] == VOCABULARY for fact in model.get("extensionFacts", [])):
            continue
        if len(uses) != 1 or any(uses[0].get(k) != v for k, v in {"version": VERSION, "schema": SCHEMA, "requirement": "required"}.items()):
            issues.append("requires exact runtime-values 0.2.0 vocabulary")
            continue
        affected = {(item.get("family"), canonical(item.get("scope"))) for item in uses[0]["affects"] if item["kind"] == "fact-family"}
        records: dict[str, dict[str, dict]] = {family: {} for family in FAMILIES}
        for fact in model.get("extensionFacts", []):
            if fact["vocabulary"] != VOCABULARY:
                continue
            family = fact["family"]
            if fact["version"] != VERSION or family not in FAMILIES:
                issues.append("unknown family/version")
                continue
            value = fact["payload"]
            if not validator.is_valid(value):
                issues.append("invalid payload structure")
                continue
            kind, field = FAMILIES[family]
            if value["kind"] != kind:
                issues.append("family/kind mismatch")
                continue
            identity = value[field]
            scope = {field: identity}
            if fact["scope"] != scope or (family, canonical(scope)) not in affected:
                issues.append("fact scope/affects mismatch")
            refs = fact.get("provenance", [document.get("defaultProvenance")])
            if not refs or any(ref not in provenance for ref in refs):
                issues.append("unresolved fact provenance")
            if identity in records[family]:
                issues.append("duplicate local record identity")
            records[family][identity] = value
            issues.extend(payload_issues(value))
        if issues:
            continue
        contracts, targets, activations, bindings, observations = (records[family] for family in FAMILIES)
        for contract in contracts.values():
            for selector in contract["definition"]["applicability"]["selectors"]:
                if not any(selector_match(outer, selector) == "matched" or outer == selector for outer in model["artifactSelectors"]):
                    issues.append("contract selector exceeds enclosing model applicability")
        for statement in model.get("completenessStatements", []):
            if statement.get("vocabulary") != VOCABULARY:
                continue
            family = statement["family"]
            if statement.get("version") != VERSION or family not in FAMILIES or (family, canonical(statement["scope"])) not in affected:
                issues.append("unresolved completeness scope/version")
                continue
            field = FAMILIES[family][1]
            record = records[family].get(statement["scope"].get(field))
            if record is None:
                issues.append("completeness scope has no runtime record")
            elif statement["status"] == "complete":
                coverage = (record["definition"].get("coverage") if family == "runtime-targets" else record["definition"]["behavior"]["coverage"] if family == "runtime-contracts" else record.get("coverage"))
                if family == "runtime-activations":
                    if record["candidateCoverage"]["status"] != "complete" or record["outcome"] not in {"matched", "not-matched", "disabled"}:
                        issues.append("complete activation family contains unresolved activation")
                elif not coverage or coverage["status"] != "complete":
                    issues.append("complete family contradicts record coverage")
        for activation in activations.values():
            if activation["targetId"] not in targets or any(name not in contracts for name in activation["candidateIds"]):
                issues.append("unresolved activation target/candidates")
                continue
            expected_candidates = {name for name, item in contracts.items() if item["definition"]["surface"] == activation["surface"]}
            if set(activation["candidateIds"]) != expected_candidates:
                issues.append("candidate inventory omits or includes wrong-surface contracts")
            if not set(activation["disabledIds"]).issubset(activation["candidateIds"]):
                issues.append("disabled candidate does not resolve")
            if activation["activationDigest"] != digest(activation_input(activation, contracts, targets)):
                issues.append("activation digest mismatch")
            # Consistency only: consumers must receive this digest from external policy.
            outcome, selected = evaluate_activation(activation, contracts, targets, digest(activation["policy"]))
            if activation["outcome"] != outcome or sorted(activation["selectedIds"]) != selected:
                issues.append(f"activation result mismatch: expected {outcome} {selected}")
        for binding in bindings.values():
            activation = activations.get(binding["activationId"])
            contract = contracts.get(binding["contractId"])
            if activation is None or contract is None or activation["targetId"] not in targets:
                issues.append("unresolved binding activation/contract")
                continue
            target = targets[activation["targetId"]]
            if binding["activationDigest"] != activation["activationDigest"]:
                issues.append("binding activation snapshot mismatch")
            if {k: binding["source"][k] for k in ("resource", "resourceDigest")} not in target["definition"]["resources"]:
                issues.append("binding source outside target partition")
            if binding["outcome"] == "exact" and (activation["outcome"] != "matched" or binding["contractId"] not in activation["selectedIds"] or binding["language"] not in contract["definition"]["languages"]):
                issues.append("exact binding requires active interpreted contract/language")
        for observation in observations.values():
            binding = bindings.get(observation["bindingId"])
            if binding is None or binding["contractId"] not in contracts or binding["activationId"] not in activations:
                issues.append("unresolved observation binding")
                continue
            activation = activations[binding["activationId"]]
            if activation["targetId"] not in targets:
                continue
            target = targets[activation["targetId"]]
            behavior = contracts[binding["contractId"]]["definition"]["behavior"]
            source = observation["source"]
            if any(source[field] != binding["source"][field] for field in ("resource", "resourceDigest")):
                issues.append("observation and binding source disagree")
            if not (source["startByte"] <= binding["source"]["startByte"] < binding["source"]["endByte"] <= source["endByte"]):
                issues.append("binding occurrence is outside observed expression")
            if observation["baseValue"] != binding["container"] or observation["store"]["container"] != binding["container"]:
                issues.append("observation container/base identity does not join binding")
            for field, kind in (("invocation", "invocation"), ("realm", "realm"), ("backing", "store")):
                identity = observation["store"][field]
                if identity["kind"] != kind:
                    issues.append("store identity kind mismatch")
            store = observation["store"]
            if store["relationship"] == "copied" and (store["copiedFrom"]["kind"] != "store" or store["copyPoint"]["kind"] != "point" or store["copiedFrom"] == store["backing"]):
                issues.append("copied store lacks distinct backing identity and copy boundary")
            realm = target["definition"]["context"]["realm"]
            if realm == "worker-shared" and store["relationship"] not in {"shared", "unknown"}:
                issues.append("shared worker cannot claim isolated/copied environment")
            key = observation["key"]
            if key["kind"] in {"property", "index"} and behavior["keyDomain"] != "static-" + key["kind"]:
                issues.append("observation key is outside behavior domain")
            if observation["proof"]["normal"] == "exact" and binding["outcome"] != "exact":
                issues.append("exact load requires exact root/container binding")
            lookup = observation["proof"]["lookup"]
            if lookup.startswith("mapping") and behavior["lookup"] != "mapping-entry":
                issues.append("mapping proof cannot satisfy own-value behavior")
            if lookup in {"own-present", "absent-no-fallback"} and behavior["lookup"] != "own-value":
                issues.append("own-value proof cannot satisfy mapping behavior")
            if observation["origin"] == "initial-if-present" and lookup not in {"own-present", "mapping-present", "unknown"}:
                issues.append("initial origin lacks initial entry lookup")
            if observation["coverage"]["status"] == "complete":
                if binding["coverage"]["status"] != "complete" or behavior["coverage"]["status"] != "complete":
                    issues.append("complete observation requires complete binding and behavior")
                storage_key = observation.get("storageKey", {"kind": "unsupported"})
                if key_relation(storage_key, storage_key, behavior["keyEquality"]) != "equal":
                    issues.append("complete observation requires supported key equality")
            if observation["origin"] == "absent" and lookup not in {"absent-no-fallback", "mapping-absent"}:
                issues.append("absent origin lacks absence proof")
        # Duplicate facts at one exact executable point cannot contradict one another.
        observation_claims: dict[bytes, set[bytes]] = {}
        for observation in observations.values():
            binding = bindings.get(observation["bindingId"])
            if binding is None or binding["activationId"] not in activations:
                continue
            activation = activations[binding["activationId"]]
            if activation["targetId"] not in targets:
                continue
            key = canonical({
                "targetDigest": targets[activation["targetId"]]["targetDigest"],
                **{field: observation[field] for field in ("loadOperation", "point", "phase")},
                **{field: observation["store"][field] for field in ("invocation", "realm")},
            })
            claim = {field: observation.get(field) for field in ("baseValue", "resultValue", "key", "storageKey", "origin")}
            claim["proof"] = {field: value for field, value in observation["proof"].items() if field not in {"evidence", "closureDigest"}}
            claim["store"] = {field: value for field, value in observation["store"].items() if field != "evidence"}
            observation_claims.setdefault(key, set()).add(canonical(claim))
        if any(len(claims) > 1 for claims in observation_claims.values()):
            issues.append("contradictory observations at one executable point")
    return sorted(set(issues))


def main() -> int:
    core_spec = importlib.util.spec_from_file_location("csmi_core_validator", ROOT / "scripts/validate-schema.py")
    core_validator = importlib.util.module_from_spec(core_spec)
    core_spec.loader.exec_module(core_validator)
    schema = load(PROFILE / "schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    core = Draft202012Validator(load(ROOT / "spec/0.1/schema.json"), format_checker=FormatChecker())
    failures, counts = [], {}
    for group in ("valid", "invalid"):
        files = sorted((PROFILE / "fixtures" / group).glob("*.json"))
        counts[group] = len(files)
        if not files:
            failures.append(f"missing {group} payload fixtures")
        for path in files:
            value = load(path)
            if validator.is_valid(value) != (group == "valid"):
                failures.append(f"{path.name}: unexpected structural result")
    documents = []
    for group in ("valid", "semantic-invalid"):
        files = sorted((PROFILE / "fixtures/documents" / group).glob("*.json"))
        counts["documents-" + group] = len(files)
        if not files:
            failures.append(f"missing {group} documents")
        for path in files:
            value = load(path)
            issues = document_issues(value)
            if not core.is_valid(value) or any(not validator.is_valid(fact["payload"]) for model in value["semanticModels"] for fact in model.get("extensionFacts", []) if fact["vocabulary"] == VOCABULARY):
                failures.append(f"{path.name}: complete-document fixture is not structurally valid")
            if (not issues) != (group == "valid"):
                failures.append(f"{path.name}: {issues or 'unexpected acceptance'}")
            if group == "valid":
                failures.extend(f"{path.name}: {issue}" for issue in core_validator.semantic_errors(value))
                documents.append((path, value))
                if document_issues(json.loads(json.dumps(value))):
                    failures.append(f"{path.name}: round trip changed validity")
    # Unicode UTF-16 member ordering is distinct from Unicode scalar ordering.
    if canonical({"\ue000": 1, "\U00010000": 2}) != '{"\U00010000":2,"\ue000":1}'.encode():
        failures.append("JCS UTF-16 ordering")
    if digest({"set": ["b", "a"]}) != digest({"set": ["a", "b"]}):
        failures.append("set order changed digest")
    with_core = load(PROFILE / "fixtures/documents/valid/portable-node-env.json")
    unaffected = load(ROOT / "fixtures/valid/partial-summary.json")
    with_core["semanticModels"].extend(unaffected["semanticModels"])
    if document_issues(with_core):
        failures.append("unaffected core model incorrectly requires runtime vocabulary")
    alias_document = load(PROFILE / "fixtures/documents/valid/complete-proof.json")
    model = alias_document["semanticModels"][0]
    for family, field in (("runtime-bindings", "bindingId"), ("runtime-observations", "observationId")):
        fact = copy.deepcopy(next(fact for fact in model["extensionFacts"] if fact["family"] == family))
        fact["payload"][field] = "alias-" + field
        fact["scope"] = {field: fact["payload"][field]}
        if family == "runtime-observations":
            fact["payload"]["bindingId"] = "alias-bindingId"
        model["extensionFacts"].append(fact)
        model["vocabularyUses"][0]["affects"].append({"kind": "fact-family", "family": family, "scope": fact["scope"]})
    if document_issues(alias_document):
        failures.append("equivalent observation aliases were rejected")
    fact["payload"]["resultValue"]["locatorDigest"] = "f" * 64
    if "contradictory observations at one executable point" not in document_issues(alias_document):
        failures.append("local binding aliases hid contradictory exact results")
    for path, document in documents:
        older = copy.deepcopy(document)
        older["semanticModels"][0]["vocabularyUses"][0]["version"] = "0.1.0"
        if not document_issues(older):
            failures.append("version downgrade accepted")
        for model in document["semanticModels"]:
            contracts = {f["payload"]["contractId"]: f["payload"] for f in model["extensionFacts"] if f["family"] == "runtime-contracts"}
            targets = {f["payload"]["targetId"]: f["payload"] for f in model["extensionFacts"] if f["family"] == "runtime-targets"}
            for fact in model["extensionFacts"]:
                if fact["family"] == "runtime-activations" and fact["payload"]["outcome"] == "matched":
                    if evaluate_activation(fact["payload"], contracts, targets)[0] != "review-required":
                        failures.append("embedded policy self-authorized activation")
        policies = [digest(fact["payload"]["policy"]) for model in document["semanticModels"] for fact in model["extensionFacts"] if fact["family"] == "runtime-activations"]
        result = subprocess.run(["node", str(ROOT / "reference/runtime-values-consumer.mjs")],
                                input=json.dumps({"document": document, "acceptedPolicies": policies}), text=True, capture_output=True)
        if result.returncode:
            failures.append(f"{path.name}: independent consumer failed: {result.stderr.strip()}")
        else:
            expected = [{"activationId": fact["payload"]["activationId"], "outcome": fact["payload"]["outcome"],
                         "selectedIds": fact["payload"]["selectedIds"], "activationDigest": fact["payload"]["activationDigest"]}
                        for model in document["semanticModels"] for fact in model["extensionFacts"] if fact["family"] == "runtime-activations"]
            if canonical(json.loads(result.stdout)) != canonical(expected):
                failures.append(f"{path.name}: independent consumer outcome disagreement")
        reordered = copy.deepcopy(document)
        for model in reordered["semanticModels"]:
            model["extensionFacts"].reverse()
            for fact in model["extensionFacts"]:
                payload = fact["payload"]
                if payload["kind"] == "runtime-activation":
                    payload["candidateIds"].reverse()
                    payload["reviews"].reverse()
                elif payload["kind"] == "runtime-contract":
                    payload["definition"]["languages"].reverse()
        if document_issues(reordered):
            failures.append(f"{path.name}: semantic set reordering changed validity")
        if path.name == "portable-node-env.json":
            failures.extend(reference_checks(document))
    if failures:
        for failure in failures:
            print(failure, file=sys.stderr)
        return 1
    print(f"runtime-values 0.2: {counts}; independent JavaScript consumer, digest, range, evidence, round-trip and fail-closed policy checks passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
