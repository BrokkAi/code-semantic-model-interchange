#!/usr/bin/env python3
"""Validate conditional-type-refinement payloads and an independent consumer."""

from __future__ import annotations

import json
import copy
import sys
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "conditional-type-refinement" / "0.1"
VOCABULARY = "csmi.conditional-type-refinement"
VERSION = "0.1.0"
SCHEMA_ID = "https://csmi.brokk.ai/schema/profiles/conditional-type-refinement/0.1/schema.json"
FAMILY = "conditional-type-refinements"


def load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def type_symbols(expression: dict[str, Any]) -> list[tuple[str, str]]:
    kind = expression.get("kind")
    if kind == "reference":
        result = [(str(expression.get("symbol")), "type")]
        for argument in expression.get("arguments", []):
            result.extend(type_symbols(argument))
        return result
    if kind == "parameter":
        return [(str(expression.get("symbol")), "type-parameter")]
    return []


def type_intrinsics(expression: dict[str, Any]) -> list[tuple[str, str]]:
    if expression.get("kind") == "intrinsic":
        return [(str(expression.get("vocabulary")), str(expression.get("version")))]
    result: list[tuple[str, str]] = []
    for argument in expression.get("arguments", []):
        result.extend(type_intrinsics(argument))
    return result


def payload_issues(payload: dict[str, Any], declarations: dict[str, dict[str, Any]]) -> list[str]:
    issues: list[str] = []
    callable_id = payload.get("callable")
    declaration = declarations.get(str(callable_id), {})
    if declaration.get("category") != "callable":
        issues.append("callable must resolve to one local callable declaration")
        return issues
    shape = declaration.get("callable")
    if not isinstance(shape, dict):
        issues.append("callable shape must be available")
        return issues
    positions = [item.get("position") for item in shape.get("parameters", []) if isinstance(item, dict)]
    subject_position = payload.get("subject", {}).get("position")
    if subject_position not in positions:
        issues.append("subject parameter ordinal must exist in the exact callable shape")
    outcome = payload.get("outcome", {})
    if outcome.get("kind") == "supported":
        for symbol, expected_category in type_symbols(outcome["target"]):
            if declarations.get(symbol, {}).get("category") != expected_category:
                issues.append(f"target {symbol} must resolve to a local {expected_category} declaration")
    return issues


def candidate_issues(payloads: list[dict[str, Any]]) -> list[str]:
    by_scope: dict[tuple[str, str], set[str]] = {}
    for payload in payloads:
        key = (str(payload.get("callable")), canonical(payload.get("subject")))
        by_scope.setdefault(key, set()).add(canonical(payload.get("outcome")))
    return ["conflicting candidates for exact callable and subject scope" for values in by_scope.values() if len(values) > 1]


def document_issues(document: dict[str, Any]) -> list[str]:
    issues: list[str] = []
    provenance_ids = {record.get("id") for record in document.get("provenanceRecords", [])}
    default_provenance = document.get("defaultProvenance")
    for model in document.get("semanticModels", []):
        declarations = {item.get("symbol"): item for item in model.get("declarations", [])}
        declared_required_uses = {
            (use.get("identifier"), use.get("version"))
            for use in model.get("vocabularyUses", [])
            if use.get("requirement") == "required"
        }
        required_use_affects = {
            (use.get("identifier"), use.get("version")): {
                (item.get("family"), canonical(item.get("scope")))
                for item in use.get("affects", []) if item.get("kind") == "fact-family"
            }
            for use in model.get("vocabularyUses", []) if use.get("requirement") == "required"
        }
        callable_shape_complete = {
            statement.get("scope", {}).get("symbol")
            for statement in model.get("completenessStatements", [])
            if statement.get("family") == "declaration-aspects"
            and statement.get("scope", {}).get("aspect") == "callable-shape"
            and statement.get("status") == "complete"
        }
        uses = [use for use in model.get("vocabularyUses", []) if use.get("identifier") == VOCABULARY]
        if len(uses) != 1:
            issues.append("requires exactly one vocabulary use")
            affected: set[tuple[str, str]] = set()
        else:
            use = uses[0]
            if use.get("version") != VERSION or use.get("schema") != SCHEMA_ID or use.get("requirement") != "required":
                issues.append("vocabulary use must have exact version/schema and be required")
            affected = {
                (item.get("family"), canonical(item.get("scope")))
                for item in use.get("affects", []) if item.get("kind") == "fact-family"
            }
        facts_by_key: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for fact in model.get("extensionFacts", []):
            if fact.get("vocabulary") != VOCABULARY:
                continue
            payload = fact.get("payload", {})
            expected_scope = {"callable": payload.get("callable"), "subject": payload.get("subject")}
            key = (FAMILY, canonical(expected_scope))
            if fact.get("version") != VERSION or fact.get("family") != FAMILY or fact.get("scope") != expected_scope:
                issues.append("fact version, family, or exact scope mismatch")
            if key not in affected:
                issues.append("fact exact scope absent from affects")
            references = fact.get("provenance") or ([default_provenance] if default_provenance else [])
            if not references or any(reference not in provenance_ids for reference in references):
                issues.append("fact provenance must resolve")
            if payload.get("callable") not in callable_shape_complete:
                issues.append("callable shape must have complete declaration-aspect coverage")
            issues.extend(payload_issues(payload, declarations))
            outcome = payload.get("outcome", {})
            if outcome.get("kind") == "supported":
                for intrinsic in type_intrinsics(outcome["target"]):
                    if intrinsic not in declared_required_uses:
                        issues.append("target intrinsic must have an exact required vocabulary use")
                    elif key not in required_use_affects.get(intrinsic, set()):
                        issues.append("target intrinsic vocabulary must affect the exact refinement scope")
            facts_by_key.setdefault(key, []).append(payload)
        for candidates in facts_by_key.values():
            if len({canonical(item.get("outcome")) for item in candidates}) > 1:
                issues.append("conflicting candidates for exact callable and subject scope")
        seen = set()
        for statement in model.get("completenessStatements", []):
            if statement.get("vocabulary") != VOCABULARY:
                continue
            key = (statement.get("family"), canonical(statement.get("scope")))
            if statement.get("version") != VERSION or statement.get("family") != FAMILY or key not in affected:
                issues.append("completeness version/family/scope mismatch")
            if key in seen:
                issues.append("duplicate completeness scope")
            seen.add(key)
            candidates = facts_by_key.get(key, [])
            closed = any(item.get("outcome", {}).get("kind") != "supported" for item in candidates)
            conflict = len({canonical(item.get("outcome")) for item in candidates}) > 1
            if statement.get("status") == "complete" and (closed or conflict or not candidates):
                issues.append("complete scope contains unsupported, indeterminate, conflict, or no fact")
    return issues


def consume_branch(payloads: list[dict[str, Any]], callable_id: str, position: int, truthy: bool) -> dict[str, Any]:
    """Consume only the portable wire contract; never collapse uncertainty to no-op."""
    matches = [
        payload for payload in payloads
        if payload.get("callable") == callable_id
        and payload.get("subject") == {"kind": "parameter", "position": position}
    ]
    if len(matches) != 1:
        return {"kind": "uninterpretable", "reason": "missing-or-conflicting-candidates"}
    outcome = matches[0]["outcome"]
    if outcome["kind"] != "supported":
        return {"kind": "uninterpretable", "reason": outcome["limitation"]["kind"]}
    if truthy:
        return {"kind": "include", "target": outcome["target"]}
    if outcome["semantics"] == "biconditional":
        return {"kind": "exclude", "target": outcome["target"]}
    return {"kind": "unchanged"}


def consume_document(
    document: dict[str, Any], supported_versions: set[str], truthy: bool,
    supported_vocabularies: set[tuple[str, str]] | None = None,
) -> dict[str, Any]:
    model = document["semanticModels"][0]
    use = next((item for item in model.get("vocabularyUses", []) if item.get("identifier") == VOCABULARY), None)
    if use is None or use.get("version") not in supported_versions or use.get("requirement") != "required":
        return {"kind": "uninterpretable", "reason": "unsupported-required-vocabulary"}
    if document_issues(document):
        return {"kind": "uninterpretable", "reason": "invalid-profile-join"}
    facts = [item for item in model["extensionFacts"] if item.get("vocabulary") == VOCABULARY]
    fact = facts[0]
    scope = fact["scope"]
    payloads = [item["payload"] for item in facts if item.get("scope") == scope]
    supported_vocabularies = supported_vocabularies or {(VOCABULARY, VERSION)}
    for payload in payloads:
        outcome = payload.get("outcome", {})
        if outcome.get("kind") == "supported":
            if any(intrinsic not in supported_vocabularies for intrinsic in type_intrinsics(outcome["target"])):
                return {"kind": "uninterpretable", "reason": "unsupported-target-vocabulary"}
    return consume_branch(payloads, scope["callable"], scope["subject"]["position"], truthy)


def main() -> int:
    schema = load(PROFILE / "schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    core_validator = Draft202012Validator(load(ROOT / "spec" / "0.1" / "schema.json"), format_checker=FormatChecker())
    declarations = {
        "is_text_sequence": {"category": "callable", "callable": {"parameters": [{"position": 0}]}},
        "is_text": {"category": "callable", "callable": {"parameters": [{"position": 0}]}},
        "has_dynamic_shape": {"category": "callable", "callable": {"parameters": [{"position": 0}, {"position": 1}]}},
        "Sequence": {"category": "type"},
        "Text": {"category": "type"},
    }
    counts: dict[str, int] = {}
    valid_payloads: dict[str, dict[str, Any]] = {}
    for group in ("valid", "invalid", "semantic-invalid"):
        paths = sorted((PROFILE / "fixtures" / group).glob("*.json"))
        assert paths, f"no {group} fixtures"
        counts[group] = len(paths)
        for path in paths:
            value = load(path)
            if group == "semantic-invalid" and isinstance(value, list):
                assert all(not list(validator.iter_errors(item)) for item in value), path
                assert candidate_issues(value), path
                continue
            errors = list(validator.iter_errors(value))
            if group == "invalid":
                assert errors, (path, "expected structural rejection")
                continue
            assert not errors, (path, errors)
            issues = payload_issues(value, declarations)
            if group == "semantic-invalid":
                assert issues, (path, "expected semantic rejection")
            else:
                assert not issues, (path, issues)
                valid_payloads[path.stem] = value

    type_is = valid_payloads["type-is-sequence-text"]
    type_guard = valid_payloads["type-guard-text"]
    unsupported = valid_payloads["unsupported-target"]
    assert consume_branch([type_is], "is_text_sequence", 0, True)["kind"] == "include"
    assert consume_branch([type_is], "is_text_sequence", 0, False)["kind"] == "exclude"
    assert consume_branch([type_guard], "is_text", 0, True)["kind"] == "include"
    assert consume_branch([type_guard], "is_text", 0, False) == {"kind": "unchanged"}
    assert consume_branch([unsupported], "has_dynamic_shape", 1, True) == {
        "kind": "uninterpretable", "reason": "unsupported-target"
    }
    assert consume_branch([type_guard, {**type_guard, "outcome": unsupported["outcome"]}], "is_text", 0, True) == {
        "kind": "uninterpretable", "reason": "missing-or-conflicting-candidates"
    }
    assert consume_branch([], "is_text", 0, True)["kind"] == "uninterpretable"
    documents = {path.stem: load(path) for path in sorted((PROFILE / "fixtures" / "documents").glob("*.json"))}
    assert set(documents) == {"complete-biconditional", "complete-positive-only", "partial-unsupported"}
    for path_name, document in documents.items():
        assert not list(core_validator.iter_errors(document)), path_name
        assert not document_issues(document), (path_name, document_issues(document))
    assert consume_document(documents["complete-biconditional"], {VERSION}, False)["kind"] == "exclude"
    assert consume_document(documents["complete-positive-only"], {VERSION}, False) == {"kind": "unchanged"}
    assert consume_document(documents["partial-unsupported"], {VERSION}, True)["kind"] == "uninterpretable"
    assert consume_document(documents["complete-biconditional"], {"0.0.9"}, True) == {
        "kind": "uninterpretable", "reason": "unsupported-required-vocabulary"
    }
    invalid_complete = json.loads(json.dumps(documents["partial-unsupported"]))
    invalid_complete["semanticModels"][0]["completenessStatements"][0] = {
        **invalid_complete["semanticModels"][0]["completenessStatements"][0], "status": "complete"
    }
    invalid_complete["semanticModels"][0]["completenessStatements"][0].pop("limitations")
    assert "complete scope contains unsupported, indeterminate, conflict, or no fact" in document_issues(invalid_complete)
    bad_use = copy.deepcopy(documents["complete-biconditional"])
    bad_use["semanticModels"][0]["vocabularyUses"][0]["schema"] = "https://example.invalid/schema.json"
    assert "vocabulary use must have exact version/schema and be required" in document_issues(bad_use)
    bad_affects = copy.deepcopy(documents["complete-biconditional"])
    bad_affects["semanticModels"][0]["vocabularyUses"][0]["affects"][0]["scope"]["subject"]["position"] = 1
    assert "fact exact scope absent from affects" in document_issues(bad_affects)
    bad_provenance = copy.deepcopy(documents["complete-biconditional"])
    bad_provenance["semanticModels"][0]["extensionFacts"][0]["provenance"] = ["missing"]
    assert "fact provenance must resolve" in document_issues(bad_provenance)
    incomplete_callable = copy.deepcopy(documents["complete-biconditional"])
    incomplete_callable["semanticModels"][0]["completenessStatements"].pop()
    assert "callable shape must have complete declaration-aspect coverage" in document_issues(incomplete_callable)
    bad_target = copy.deepcopy(documents["complete-biconditional"])
    bad_target["semanticModels"][0]["extensionFacts"][0]["payload"]["outcome"]["target"]["symbol"] = "MissingType"
    assert "target MissingType must resolve to a local type declaration" in document_issues(bad_target)
    undeclared_intrinsic = copy.deepcopy(documents["complete-biconditional"])
    undeclared_intrinsic["semanticModels"][0]["extensionFacts"][0]["payload"]["outcome"]["target"] = {
        "kind": "intrinsic", "vocabulary": "example.types", "version": "1.0.0", "identifier": "text"
    }
    assert "target intrinsic must have an exact required vocabulary use" in document_issues(undeclared_intrinsic)
    declared_intrinsic = copy.deepcopy(undeclared_intrinsic)
    declared_intrinsic["semanticModels"][0]["vocabularyUses"].append({
        "identifier": "example.types", "version": "1.0.0", "requirement": "required",
        "affects": [{
            "kind": "fact-family", "family": FAMILY,
            "scope": declared_intrinsic["semanticModels"][0]["extensionFacts"][0]["scope"],
        }],
    })
    assert not document_issues(declared_intrinsic)
    assert consume_document(declared_intrinsic, {VERSION}, True) == {
        "kind": "uninterpretable", "reason": "unsupported-target-vocabulary"
    }
    assert consume_document(
        declared_intrinsic, {VERSION}, True,
        {(VOCABULARY, VERSION), ("example.types", "1.0.0")},
    )["kind"] == "include"
    conflict = copy.deepcopy(documents["complete-biconditional"])
    alternate = copy.deepcopy(conflict["semanticModels"][0]["extensionFacts"][0])
    alternate["payload"]["outcome"]["semantics"] = "positive-only"
    conflict["semanticModels"][0]["extensionFacts"].append(alternate)
    assert "conflicting candidates for exact callable and subject scope" in document_issues(conflict)
    assert "complete scope contains unsupported, indeterminate, conflict, or no fact" in document_issues(conflict)
    open_conflict = copy.deepcopy(conflict)
    open_conflict["semanticModels"][0]["completenessStatements"] = [
        item for item in open_conflict["semanticModels"][0]["completenessStatements"]
        if item.get("family") == "declaration-aspects"
    ]
    assert "conflicting candidates for exact callable and subject scope" in document_issues(open_conflict)
    assert consume_document(open_conflict, {VERSION}, True) == {
        "kind": "uninterpretable", "reason": "invalid-profile-join"
    }
    indeterminate = copy.deepcopy(documents["complete-biconditional"])
    indeterminate["semanticModels"][0]["extensionFacts"][0]["payload"]["outcome"] = {
        "kind": "indeterminate", "limitation": {"kind": "uninterpretable-semantics"}
    }
    assert "complete scope contains unsupported, indeterminate, conflict, or no fact" in document_issues(indeterminate)
    print(
        f"conditional type refinement: {counts}; exact subject/type resolution, "
        "TypeIs/TypeGuard branch distinction, three core-valid document joins, completeness, "
        "and fail-closed/unsupported-version consumer cases passed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
