#!/usr/bin/env python3
"""Validate runtime-values structure and normative semantic invariants."""

from __future__ import annotations

import json
import copy
import hashlib
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "runtime-values" / "0.1"
DOCUMENT = ROOT / "fixtures" / "valid" / "runtime-values.json"
SCHEMA_URI = "https://csmi.brokk.ai/schema/profiles/runtime-values/0.1/schema.json"
FAMILIES = {
    "runtime-global-exposures": ("runtime-global-exposure", "exposureId"),
    "keyed-read-behaviors": ("keyed-read-behavior", "behaviorId"),
    "runtime-global-binding-evidence": ("runtime-global-binding-evidence", "bindingEvidenceId"),
    "keyed-read-observations": ("keyed-read-observation", "observationId"),
}


def semantic_errors(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["payload is not an object"]
    errors: list[str] = []
    for field in ("rootOccurrence", "expression"):
        source_range = value.get(field)
        if isinstance(source_range, dict) and source_range.get("endByte", 0) <= source_range.get("startByte", 0):
            errors.append(f"{field} must be non-empty")
    if value.get("kind") == "runtime-global-binding-evidence" and value.get("coverage", {}).get("status") == "complete":
        if value.get("activation", {}).get("outcome") == "matched":
            if value.get("lexicalBinding") != "absent" or value.get("rebinding") != "excluded":
                errors.append("complete matched global binding requires absent lexical binding and excluded rebinding")
        elif value.get("activation", {}).get("outcome") != "not-matched" or value.get("lexicalBinding") != "present":
            errors.append("complete binding evidence requires a matched exact binding or conclusive lexical exclusion")
    if value.get("kind") == "keyed-read-observation":
        key_kind = value.get("key", {}).get("kind")
        source_form = value.get("sourceForm")
        if source_form == "dot" and key_kind != "property":
            errors.append("dot source form requires a property key")
        if source_form == "bracket-number" and key_kind != "index":
            errors.append("numeric bracket source form requires an index key")
        if value.get("normalOutcome") == "exact" and value.get("phase") != "after-effects":
            errors.append("exact normal load result must be observed after effects")
        if value.get("coverage", {}).get("status") == "complete" and (
            value.get("normalOutcome") != "exact"
            or value.get("exceptionOutcome") not in ("excluded", "possible")
            or value.get("sourceOrigin") == "indeterminate"
        ):
            errors.append("complete observation requires exact normal, interpreted exceptional, and determined origin outcomes")
    if value.get("kind") == "keyed-read-behavior" and value.get("coverage", {}).get("status") == "complete":
        if (
            value.get("exceptionBehavior") == "unknown"
            or value.get("mutationModel") == "unknown"
            or value.get("materialization") == "unknown"
        ):
            errors.append("complete behavior requires interpreted exception, mutation, and materialization semantics")
    return errors


def document_errors(document: object, validator: Draft202012Validator) -> list[str]:
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["representative document is not an object"]
    for model_index, model in enumerate(document.get("semanticModels", [])):
        uses = [use for use in model.get("vocabularyUses", []) if use.get("identifier") == "csmi.runtime-values"]
        if len(uses) != 1 or uses[0].get("version") != "0.1.0" or uses[0].get("schema") != SCHEMA_URI or uses[0].get("requirement") != "required":
            errors.append(f"model {model_index}: missing exact required runtime-values vocabulary use")
            continue
        affected = {(entry.get("family"), json.dumps(entry.get("scope"), sort_keys=True)) for entry in uses[0].get("affects", []) if entry.get("kind") == "fact-family"}
        records: dict[str, dict[str, dict]] = {family: {} for family in FAMILIES}
        for fact in model.get("extensionFacts", []):
            if fact.get("vocabulary") != "csmi.runtime-values":
                continue
            family = fact.get("family")
            if fact.get("version") != "0.1.0" or family not in FAMILIES:
                errors.append(f"model {model_index}: unknown runtime-values family or version")
                continue
            payload = fact.get("payload")
            structural = list(validator.iter_errors(payload))
            if structural:
                errors.append(f"model {model_index}: invalid {family} payload: {structural[0].message}")
                continue
            for semantic_error in semantic_errors(payload):
                errors.append(f"model {model_index}: invalid {family} semantics: {semantic_error}")
            kind, identity_field = FAMILIES[family]
            identity = payload.get(identity_field)
            expected_scope = {identity_field: identity}
            if payload.get("kind") != kind or fact.get("scope") != expected_scope:
                errors.append(f"model {model_index}: {family} kind/scope identity mismatch")
            if (family, json.dumps(expected_scope, sort_keys=True)) not in affected:
                errors.append(f"model {model_index}: {family} scope missing from vocabulary affects")
            if identity in records[family]:
                errors.append(f"model {model_index}: conflicting duplicate {family} identity {identity}")
            records[family][identity] = payload
        exposures = records["runtime-global-exposures"]
        behaviors = records["keyed-read-behaviors"]
        bindings = records["runtime-global-binding-evidence"]
        observations = records["keyed-read-observations"]
        selectors = {selector.get("purl"): {digest.get("value") for digest in selector.get("digests", [])} for selector in model.get("artifactSelectors", [])}
        enabled = [exposure for exposure in exposures.values() if exposure.get("activation") == "enabled"]
        for exposure in exposures.values():
            runtime = exposure["runtime"]
            if runtime["runtimeArtifactDigest"] not in selectors.get(runtime["runtimeArtifact"], set()):
                errors.append(f"model {model_index}: exposure runtime artifact/digest does not match model applicability")
        for behavior in behaviors.values():
            exposure = exposures.get(behavior["exposureId"])
            if exposure is None or behavior["containerMember"] not in exposure.get("members", []):
                errors.append(f"model {model_index}: behavior exposure/container reference does not resolve")
        for binding in bindings.values():
            exposure = exposures.get(binding["exposureId"])
            if exposure is None or binding["activation"]["exposureId"] != binding["exposureId"]:
                errors.append(f"model {model_index}: binding exposure identity does not resolve")
            elif (
                binding["activation"]["runtimeProfileDigest"] != exposure["runtimeProfileDigest"]
                or binding["activation"]["modelDigest"] != exposure["evidence"]["inputsDigest"]
            ):
                errors.append(f"model {model_index}: activation profile/model digests do not join the exposure")
            active_ids = sorted(item["exposureId"] for item in enabled)
            expected_active_digest = hashlib.sha256(json.dumps(active_ids, separators=(",", ":")).encode()).hexdigest()
            if binding["activation"]["activeExposureIds"] != active_ids or binding["activation"]["activeSetDigest"] != expected_active_digest:
                errors.append(f"model {model_index}: active-set identity does not match enabled exposures")
            if binding["activation"]["outcome"] == "matched" and (exposure not in enabled or len(enabled) != 1):
                errors.append(f"model {model_index}: matched activation requires one unique enabled exposure")
        for observation in observations.values():
            binding = bindings.get(observation["bindingEvidenceId"])
            behavior = behaviors.get(observation["behaviorId"])
            if binding is None or behavior is None or behavior["exposureId"] != binding["exposureId"]:
                errors.append(f"model {model_index}: observation references do not join in one exposure")
                continue
            key_kind = observation["key"]["kind"]
            expected = "static-property" if key_kind == "property" else "static-index"
            if behavior["acceptedKeys"] != expected:
                errors.append(f"model {model_index}: observation key is not accepted by behavior")
            if observation.get("sourceForm") == "bracket-string" and key_kind != "property":
                errors.append(f"model {model_index}: bracket-string requires property behavior")
            if observation["expression"]["resourceDigest"] != binding["rootOccurrence"]["resourceDigest"]:
                errors.append(f"model {model_index}: binding and observation source artifacts differ")
            owner_digests = {
                observation[field]["ownerDigest"]
                for field in ("baseValue", "loadOperation", "resultValue", "observationPoint")
            }
            if owner_digests != {observation["expression"]["resourceDigest"]}:
                errors.append(f"model {model_index}: operation/value/point identities do not share the source owner")
            expected_kinds = {"baseValue": "value", "loadOperation": "operation", "resultValue": "value", "observationPoint": "point"}
            if any(observation[field]["kind"] != kind for field, kind in expected_kinds.items()):
                errors.append(f"model {model_index}: scoped identity kind does not match its semantic field")
            if binding["scopeIdentity"]["kind"] != "scope":
                errors.append(f"model {model_index}: scope identity has the wrong kind")
            if binding["scopeIdentity"]["ownerDigest"] != binding["rootOccurrence"]["resourceDigest"]:
                errors.append(f"model {model_index}: scope identity does not share the binding source owner")
            if observation["sourceOrigin"] == "pristine-runtime-input" and (
                behavior["mutationModel"] != "pristine-input-until-write"
                or binding["rebinding"] != "excluded"
                or binding["coverage"]["status"] != "complete"
            ):
                errors.append(f"model {model_index}: pristine origin lacks complete binding/mutation contract")
            if observation["coverage"]["status"] == "complete" and behavior["coverage"]["status"] != "complete":
                errors.append(f"model {model_index}: complete observation requires complete behavior contract")
    return errors


def main() -> int:
    schema = json.loads((PROFILE / "schema.json").read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = 0
    counts = {"valid": 0, "invalid": 0, "semantic-invalid": 0}
    for group in counts:
        paths = sorted((PROFILE / "fixtures" / group).glob("*.json"))
        if not paths:
            print(f"runtime-values: missing {group} fixtures", file=sys.stderr)
            failures += 1
        for path in paths:
            counts[group] += 1
            value = json.loads(path.read_text(encoding="utf-8"))
            structural = list(validator.iter_errors(value))
            semantic = [] if structural else semantic_errors(value)
            accepted = not structural and not semantic
            expected = group == "valid"
            if accepted != expected:
                detail = structural[0].message if structural else semantic[0] if semantic else "unexpectedly accepted"
                print(f"{path.relative_to(ROOT)}: {detail}", file=sys.stderr)
                failures += 1
            if group == "semantic-invalid" and structural:
                print(f"{path.relative_to(ROOT)}: expected structural validity", file=sys.stderr)
                failures += 1
    document = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    core_schema = json.loads((ROOT / "spec" / "0.1" / "schema.json").read_text(encoding="utf-8"))
    core_errors = list(Draft202012Validator(core_schema, format_checker=FormatChecker()).iter_errors(document))
    integration_errors = document_errors(document, validator) if not core_errors else [core_errors[0].message]
    for error in integration_errors:
        print(f"{DOCUMENT.relative_to(ROOT)}: {error}", file=sys.stderr)
        failures += 1
    negative_cases = []
    missing_reference = copy.deepcopy(document)
    missing_reference["semanticModels"][0]["extensionFacts"][-1]["payload"]["behaviorId"] = "missing-behavior"
    negative_cases.append(("missing cross-record reference", missing_reference))
    wrong_scope = copy.deepcopy(document)
    wrong_scope["semanticModels"][0]["extensionFacts"][-1]["scope"]["observationId"] = "wrong-observation"
    negative_cases.append(("fact scope mismatch", wrong_scope))
    wrong_artifact = copy.deepcopy(document)
    wrong_artifact["semanticModels"][0]["extensionFacts"][0]["payload"]["runtime"]["runtimeArtifactDigest"] = "f" * 64
    negative_cases.append(("runtime applicability mismatch", wrong_artifact))
    duplicate_exposure = copy.deepcopy(document)
    duplicate = copy.deepcopy(duplicate_exposure["semanticModels"][0]["extensionFacts"][0])
    duplicate["payload"]["exposureId"] = "node-process-other"
    duplicate["scope"]["exposureId"] = "node-process-other"
    duplicate_exposure["semanticModels"][0]["extensionFacts"].append(duplicate)
    negative_cases.append(("non-unique enabled activation", duplicate_exposure))
    for name, candidate in negative_cases:
        if not document_errors(candidate, validator):
            print(f"runtime-values negative integration case unexpectedly accepted: {name}", file=sys.stderr)
            failures += 1
    if failures:
        return 1
    print(
        "Runtime-values validation passed: "
        f"{counts['valid']} valid, {counts['invalid']} structurally rejected, "
        f"{counts['semantic-invalid']} semantic-invalid rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
