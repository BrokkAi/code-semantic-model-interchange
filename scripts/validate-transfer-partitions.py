#!/usr/bin/env python3
"""Independent, bounded consumer for transfer-partition conformance cases."""
from __future__ import annotations

import copy
import json
from pathlib import Path

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ("csmi.transfer-partitions", "0.1.0")
URI = "https://csmi.brokk.ai/schema/profiles/transfer-partitions/0.1/schema.json"
FAMILY = "transfer-partitions"
SCOPE_SCHEMA = json.loads((ROOT / "profiles/transfer-partitions/0.1/schema.json").read_text())
CORE_SCHEMA = json.loads((ROOT / "spec/0.1/schema.json").read_text())


def scope_key(scope):
    return json.dumps(scope, sort_keys=True, separators=(",", ":"))


def in_partition(scope, edge):
    source = edge["source"]["root"]
    destination = edge["destination"]["root"]
    return (destination == scope["destination"] and
            (scope["source"]["kind"] == "all-inputs" or
             source == scope["source"]["root"]))


def covers(claim, requested):
    return (claim["callable"] == requested["callable"] and
            claim["destination"] == requested["destination"] and
            (claim["source"] == requested["source"] or
             claim["source"]["kind"] == "all-inputs"))


def scope_valid_for_shape(scope, shape, symbols):
    if scope["destination"]["position"] not in {r["position"] for r in shape.get("results", [])}:
        return False
    source = scope["source"]
    if source["kind"] == "all-inputs":
        return True
    root = source["root"]
    return ((root["role"] == "parameter" and root["position"] in
             {p["position"] for p in shape.get("parameters", [])}) or
            (root["role"] == "receiver" and "receiver" in shape) or
            (root["role"] == "capture" and
             symbols.get(root["symbol"], {}).get("category") == "value"))


def consume(document, requested, candidate, supported=True):
    """Return a typed outcome. Candidate is one *core* transfer, not an effect."""
    if not supported:
        return "uninterpretable"
    if list(Draft202012Validator(CORE_SCHEMA).iter_errors(document)):
        return "invalid"
    if list(Draft202012Validator(SCOPE_SCHEMA).iter_errors(requested)):
        return "invalid"
    models = document["semanticModels"]
    if len(models) != 1:  # this reference consumer accepts one matched model
        return "indeterminate"
    model = models[0]
    claims = [c for c in model.get("completenessStatements", [])
              if c.get("vocabulary") == PROFILE[0] and c.get("family") == FAMILY]
    symbols = {d["symbol"]: d for d in model.get("declarations", [])}
    declarations = {d["symbol"]: d for d in model.get("declarations", [])}
    summaries = [s for s in model.get("procedureSummaries", [])
                 if s["callable"] == requested["callable"]]
    if requested["callable"] not in {s["id"] for s in model.get("symbols", [])} or len(summaries) != 1:
        return "invalid"
    declaration = declarations.get(requested["callable"])
    if not declaration or declaration["category"] != "callable":
        return "invalid"
    shape = declaration["callable"]
    if not scope_valid_for_shape(requested, shape, symbols):
        return "invalid"
    uses = [u for u in model.get("vocabularyUses", []) if
            (u["identifier"], u["version"]) == PROFILE]
    seen = set()
    for claim in claims:
        scope = claim["scope"]
        if claim.get("version") != PROFILE[1] or list(Draft202012Validator(SCOPE_SCHEMA).iter_errors(scope)):
            return "uninterpretable" if claim.get("version") != PROFILE[1] else "invalid"
        if scope["callable"] != requested["callable"] or not scope_valid_for_shape(scope, shape, symbols):
            return "invalid"
        key = scope_key(scope)
        if key in seen:
            return "invalid"
        seen.add(key)
        if not any(u["schema"] == URI and u["requirement"] == "required" and
                   {"kind": "fact-family", "family": FAMILY, "scope": scope} in u["affects"]
                   for u in uses):
            return "invalid"
    if not in_partition(requested, candidate):
        return "out-of-scope"
    # This small consumer supports whole roots only. A projected edge might
    # subsume a candidate under a separately required projection profile.
    # Without that algebra it cannot license any negative inference.
    if ("projection" in candidate["source"] or "projection" in candidate["destination"] or
        any("projection" in edge["source"] or "projection" in edge["destination"]
            for edge in summaries[0].get("transfers", []) if in_partition(requested, edge))):
        return "uninterpretable"
    # A positive core edge remains usable even when coverage is partial.
    if candidate in summaries[0].get("transfers", []):
        return "may-flow"
    applicable = [c for c in claims if covers(c["scope"], requested)]
    if any(c["status"] == "complete" for c in applicable):
        return "no-reported-flow"
    if any(c["status"] == "partial" for c in applicable):
        return "partial"
    return "unknown"


def combine(documents, requested, candidate):
    """Combine exact matching single-callable documents, retaining positives."""
    models = [d["semanticModels"][0] for d in documents]
    if any(m["artifactSelectors"] != models[0]["artifactSelectors"] for m in models[1:]):
        return "indeterminate"
    symbols = [next(s for s in m["symbols"] if s["id"] == requested["callable"])
               for m in models]
    identities = [(s["scheme"], s["schemeVersion"], s["descriptors"])
                  for s in symbols]
    if any(identity != identities[0] for identity in identities[1:]):
        return "uninterpretable"
    outcomes = [consume(d, requested, candidate) for d in documents]
    if any(o in {"invalid", "uninterpretable", "indeterminate"} for o in outcomes):
        return "uninterpretable"
    if "may-flow" in outcomes:
        return "may-flow"
    if "no-reported-flow" in outcomes:
        return "no-reported-flow"
    if "partial" in outcomes:
        return "partial"
    return "unknown"


def main():
    fixtures = []
    for language in ("python", "javascript"):
        path = ROOT / f"fixtures/valid/transfer-partition-{language}.json"
        fixture = json.loads(path.read_text())
        fixtures.append(fixture)
        scope = fixture["semanticModels"][0]["completenessStatements"][1]["scope"]
        edge = {"source": {"root": {"phase": "input", "role": "parameter", "position": 0}},
                "destination": {"root": {"phase": "output", "role": "result", "position": 0}}}
        assert consume(fixture, scope, edge) == "no-reported-flow", language
        assert consume(fixture, scope, edge, supported=False) == "uninterpretable"
        projected = copy.deepcopy(edge)
        projected["source"]["projection"] = {"scheme":"unknown.projection","schemeVersion":"1","steps":[{"kind":"field"}]}
        assert consume(fixture, scope, projected) == "uninterpretable"
        # An unrelated exit, result or caller-visible state stays outside the claim.
        for role in ("exception", "parameter"):
            other = copy.deepcopy(edge)
            other["destination"]["root"] = {"phase": "output", "role": role}
            if role == "parameter":
                other["destination"]["root"]["position"] = 0
            assert consume(fixture, scope, other) == "out-of-scope"
        partial = copy.deepcopy(fixture)
        partial["semanticModels"][0]["completenessStatements"][1] = {
            **partial["semanticModels"][0]["completenessStatements"][1],
            "status": "partial", "limitations": [{"kind": "budget-exhausted"}]}
        assert consume(partial, scope, edge) == "partial"
        assert combine([partial, copy.deepcopy(partial)], scope, edge) == "partial"
        unclaimed = copy.deepcopy(fixture)
        unclaimed["semanticModels"][0]["completenessStatements"].pop()
        assert consume(unclaimed, scope, edge) == "unknown"
        positive = copy.deepcopy(partial)
        positive["semanticModels"][0]["procedureSummaries"][0]["transfers"] = [edge]
        assert consume(positive, scope, edge) == "may-flow"
        assert combine([fixture, positive], scope, edge) == "may-flow"
        assert combine([fixture, copy.deepcopy(fixture)], scope, edge) == "no-reported-flow"
        conflicting = copy.deepcopy(fixture)
        conflicting["semanticModels"][0]["symbols"][0]["descriptors"][-1]["name"] = "other"
        assert combine([fixture, conflicting], scope, edge) == "uninterpretable"
        different_artifact = copy.deepcopy(fixture)
        different_artifact["semanticModels"][0]["artifactSelectors"][0]["purl"] = "pkg:generic/other@1"
        assert combine([fixture, different_artifact], scope, edge) == "indeterminate"
        unresolved = copy.deepcopy(fixture)
        unresolved["semanticModels"][0]["completenessStatements"][1]["status"] = "partial"
        unresolved["semanticModels"][0]["completenessStatements"][1]["limitations"] = [{"kind":"input-unavailable"}]
        assert consume(unresolved, scope, edge) == "partial"
        unsupported = copy.deepcopy(fixture)
        unsupported["semanticModels"][0]["completenessStatements"][1]["version"] = "0.2.0"
        assert consume(unsupported, scope, edge) == "uninterpretable"
        duplicate = copy.deepcopy(fixture)
        duplicate["semanticModels"][0]["completenessStatements"].append(copy.deepcopy(
            duplicate["semanticModels"][0]["completenessStatements"][1]))
        assert consume(duplicate, scope, edge) == "invalid"
        missing_use = copy.deepcopy(fixture)
        missing_use["semanticModels"][0]["vocabularyUses"] = missing_use["semanticModels"][0]["vocabularyUses"][1:]
        assert consume(missing_use, scope, edge) == "invalid"
        assert covers(scope, scope)
        narrow = copy.deepcopy(scope)
        narrow["source"] = {"kind":"input-root", "root":edge["source"]["root"]}
        assert covers(scope, narrow) and not covers(narrow, scope)
        other_result = copy.deepcopy(scope)
        other_result["destination"]["position"] = 1
        assert not covers(scope, other_result) and not covers(other_result, scope)
        another_root = copy.deepcopy(narrow)
        another_root["source"]["root"]["position"] = 1
        assert not covers(narrow, another_root)
        narrow_document = copy.deepcopy(fixture)
        narrow_document["semanticModels"][0]["completenessStatements"][1]["scope"] = narrow
        narrow_document["semanticModels"][0]["vocabularyUses"][0]["affects"][0]["scope"] = narrow
        assert consume(narrow_document, scope, edge) == "unknown"
        assert consume(narrow_document, narrow, edge) == "no-reported-flow"
    print("Transfer-partition conformance passed: 2 independent language fixtures and typed near misses")


if __name__ == "__main__":
    main()
