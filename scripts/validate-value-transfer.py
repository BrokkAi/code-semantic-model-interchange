#!/usr/bin/env python3
"""Validate value-transfer payloads and their cross-record semantics."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CORE_SCHEMA = ROOT / "spec" / "0.1" / "schema.json"
PROFILE = ROOT / "profiles" / "value-transfer" / "0.1"
PROFILE_SCHEMA = PROFILE / "schema.json"
PROFILE_SCHEMA_ID = "https://csmi.brokk.ai/schema/profiles/value-transfer/0.1/schema.json"
VOCABULARY = ("csmi.value-transfer", "0.1.0")
ATTACHMENT_POINT = "procedure-summary-transfer"


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def uncertain_type_fact(payload: dict[str, object]) -> bool:
    semantics = payload.get("semantics", {})
    return isinstance(semantics, dict) and semantics.get("kind") in {"unknown", "unsupported"}


def uncertain_transfer(payload: dict[str, object]) -> bool:
    operation = payload.get("operation", {})
    transfer_kind = payload.get("transferKind", {})
    return (
        isinstance(operation, dict)
        and operation.get("kind") == "unknown"
    ) or (
        isinstance(transfer_kind, dict)
        and (
            transfer_kind.get("invalidation") == "unknown"
            or transfer_kind.get("preservation") == "unknown"
        )
    )


def semantic_issues(document: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(document, dict):
        return ["document is not an object"]

    for model_index, raw_model in enumerate(document.get("semanticModels", [])):
        if not isinstance(raw_model, dict):
            continue
        model = raw_model
        prefix = f"semanticModels[{model_index}]"
        declarations = {
            value.get("symbol"): value
            for value in model.get("declarations", [])
            if isinstance(value, dict)
        }
        uses = [
            value
            for value in model.get("vocabularyUses", [])
            if isinstance(value, dict)
            and (value.get("identifier"), value.get("version")) == VOCABULARY
        ]
        facts = [
            value
            for value in model.get("extensionFacts", [])
            if isinstance(value, dict)
            and (value.get("vocabulary"), value.get("version")) == VOCABULARY
        ]
        all_statements = [
            value
            for value in model.get("completenessStatements", [])
            if isinstance(value, dict)
        ]
        statements = [
            value
            for value in all_statements
            if (value.get("vocabulary"), value.get("version")) == VOCABULARY
        ]

        attached = []
        for summary_index, summary in enumerate(model.get("procedureSummaries", [])):
            callable_id = summary.get("callable")
            for transfer_index, transfer in enumerate(summary.get("transfers", [])):
                for extension_index, extension in enumerate(transfer.get("extensions", [])):
                    if (extension.get("vocabulary"), extension.get("version")) == VOCABULARY:
                        attached.append(
                            (
                                callable_id,
                                extension.get("payload"),
                                f"{prefix}.procedureSummaries[{summary_index}]"
                                f".transfers[{transfer_index}].extensions[{extension_index}]",
                            )
                        )
        if not (uses or facts or statements or attached):
            continue

        affected_facts: set[tuple[str, str]] = set()
        affected_attachments: set[tuple[str, str]] = set()
        if len(uses) != 1:
            issues.append(f"{prefix}: requires exactly one value-transfer vocabulary use")
        else:
            use = uses[0]
            if use.get("schema") != PROFILE_SCHEMA_ID or use.get("requirement") != "required":
                issues.append(f"{prefix}: value-transfer use must name the exact schema and be required")
            for unit in use.get("affects", []):
                if not isinstance(unit, dict):
                    continue
                if unit.get("kind") == "fact-family":
                    affected_facts.add((str(unit.get("family")), canonical(unit.get("scope"))))
                elif unit.get("kind") == "attachment":
                    affected_attachments.add(
                        (str(unit.get("attachmentPoint")), canonical(unit.get("target")))
                    )

        operations_by_symbol: dict[str, list[dict[str, object]]] = {}
        facts_by_key: dict[tuple[str, str], list[dict[str, object]]] = {}
        for fact_index, fact in enumerate(facts):
            payload = fact.get("payload")
            scope = fact.get("scope")
            family = fact.get("family")
            path = f"{prefix}.extensionFacts[{fact_index}]"
            if not isinstance(payload, dict) or not isinstance(scope, dict):
                continue
            kind = payload.get("kind")
            if kind == "type-value-semantics":
                expected_family = "type-value-semantics"
                expected_scope = {"type": payload.get("type"), "aspect": payload.get("aspect")}
                if declarations.get(payload.get("type"), {}).get("category") != "type":
                    issues.append(f"{path}: type must resolve to a local type declaration")
            elif kind == "implicit-operation":
                expected_family = "implicit-operations"
                expected_scope = {
                    "owner": payload.get("owner"),
                    "operation": payload.get("operation"),
                }
                if payload.get("operation") == "conversion-operator":
                    expected_scope["target"] = payload.get("target")
                symbol = payload.get("symbol")
                operations_by_symbol.setdefault(str(symbol), []).append(payload)
                declaration = declarations.get(symbol, {})
                if declaration.get("category") != "callable":
                    issues.append(f"{path}: symbol must resolve to a local callable declaration")
                if declaration.get("owner") != payload.get("owner"):
                    issues.append(f"{path}: callable owner does not equal the fact owner")
                if declarations.get(payload.get("owner"), {}).get("category") != "type":
                    issues.append(f"{path}: owner must resolve to a local type declaration")
                target = payload.get("target")
                if target is not None and declarations.get(target, {}).get("category") != "type":
                    issues.append(f"{path}: target must resolve to a local type declaration")
            else:
                issues.append(f"{path}: transfer payload belongs on a core transfer attachment")
                continue

            if family != expected_family:
                issues.append(f"{path}: family does not match payload kind")
                continue
            if scope != expected_scope:
                issues.append(f"{path}: scope does not exactly equal payload identity")
            key = (str(family), canonical(scope))
            if key not in affected_facts:
                issues.append(f"{path}: exact family and scope are absent from vocabulary affects")
            facts_by_key.setdefault(key, []).append(payload)

        for fact_index, fact in enumerate(facts):
            payload = fact.get("payload", {})
            if not isinstance(payload, dict) or payload.get("kind") != "type-value-semantics":
                continue
            semantics = payload.get("semantics", {})
            if not isinstance(semantics, dict) or semantics.get("kind") != "via-member":
                continue
            path = f"{prefix}.extensionFacts[{fact_index}]"
            matches = operations_by_symbol.get(str(semantics.get("member")), [])
            required_role = {
                "copy": "copy-constructor",
                "move": "move-constructor",
            }.get(payload.get("aspect"))
            if len(matches) != 1:
                issues.append(f"{path}: via-member must resolve to exactly one implicit-operation fact")
            elif matches[0].get("owner") != payload.get("type") or matches[0].get("operation") != required_role:
                issues.append(f"{path}: via-member has the wrong owner or implicit-operation role")

        uncertain_callables: set[object] = set()
        for callable_id, payload, path in attached:
            if not isinstance(payload, dict) or payload.get("kind") != "transfer":
                issues.append(f"{path}: attachment must contain a transfer payload")
                continue
            if uncertain_transfer(payload):
                uncertain_callables.add(callable_id)
            if declarations.get(callable_id, {}).get("category") != "callable":
                issues.append(f"{path}: enclosing summary callable must resolve locally")
            attachment_key = (ATTACHMENT_POINT, canonical({"callable": callable_id}))
            if attachment_key not in affected_attachments:
                issues.append(f"{path}: attachment point and callable target are absent from vocabulary affects")
            operation = payload.get("operation", {})
            if not isinstance(operation, dict) or operation.get("kind") != "implicit":
                continue
            matches = operations_by_symbol.get(str(operation.get("symbol")), [])
            if len(matches) != 1:
                issues.append(f"{path}: implicit operation must resolve to exactly one operation fact")
                continue
            transfer_kind = payload.get("transferKind", {})
            kind = transfer_kind.get("kind") if isinstance(transfer_kind, dict) else None
            allowed = {
                "copy": {"copy-constructor", "copy-assignment"},
                "aggregate-copy": {"copy-constructor", "copy-assignment"},
                "move": {"move-constructor", "move-assignment"},
                "conversion": {"conversion-operator"},
            }.get(kind)
            if allowed is not None and matches[0].get("operation") not in allowed:
                issues.append(f"{path}: implicit-operation role is incompatible with transfer kind")

        statement_keys: set[tuple[str, str]] = set()
        for statement_index, statement in enumerate(statements):
            key = (str(statement.get("family")), canonical(statement.get("scope")))
            path = f"{prefix}.completenessStatements[{statement_index}]"
            if key in statement_keys:
                issues.append(f"{path}: duplicate family and scope")
            statement_keys.add(key)
            if key not in affected_facts:
                issues.append(f"{path}: exact family and scope are absent from vocabulary affects")
            if statement.get("status") == "complete" and any(
                uncertain_type_fact(payload) for payload in facts_by_key.get(key, [])
            ):
                issues.append(f"{path}: complete coverage cannot contain unknown or unsupported type semantics")
            if (
                statement.get("status") == "complete"
                and statement.get("family") == "identity-separating-transfers"
                and statement.get("scope", {}).get("callable") in uncertain_callables
            ):
                issues.append(
                    f"{path}: complete identity-separating transfer coverage cannot contain uncertainty"
                )
    return issues


def expect_issue(document: dict[str, object], edit, expected: str) -> None:
    candidate = copy.deepcopy(document)
    edit(candidate)
    issues = semantic_issues(candidate)
    if not any(expected in issue for issue in issues):
        raise AssertionError(f"expected semantic issue containing {expected!r}, got {issues!r}")


def validator_contract_tests(valid: dict[str, object]) -> None:
    model = lambda document: document["semanticModels"][0]
    expect_issue(
        valid,
        lambda document: model(document)["extensionFacts"][0].update(
            scope={"type": "basicString", "aspect": "move"}
        ),
        "scope does not exactly equal",
    )
    expect_issue(
        valid,
        lambda document: model(document)["extensionFacts"][0]["payload"]["semantics"].update(
            member="missingMember"
        ),
        "via-member must resolve",
    )
    expect_issue(
        valid,
        lambda document: model(document)["extensionFacts"][1]["payload"].update(
            operation="copy-assignment"
        ),
        "wrong owner or implicit-operation role",
    )
    expect_issue(
        valid,
        lambda document: model(document)["procedureSummaries"][0]["transfers"][0]["extensions"][0][
            "payload"
        ]["operation"].update(symbol="missingMember"),
        "implicit operation must resolve",
    )
    expect_issue(
        valid,
        lambda document: model(document)["vocabularyUses"][0]["affects"].pop(0),
        "attachment point and callable target",
    )
    expect_issue(
        valid,
        lambda document: model(document)["procedureSummaries"][0]["transfers"][0]["extensions"][0][
            "payload"
        ].update(
            operation={
                "kind": "unknown",
                "limitation": {"kind": "unresolved-identity"},
            }
        ),
        "complete identity-separating transfer coverage cannot contain uncertainty",
    )
    expect_issue(
        valid,
        lambda document: (
            model(document)["extensionFacts"][0]["payload"].update(
                semantics={"kind": "unknown", "limitation": {"kind": "incomplete-input"}}
            ),
            model(document)["completenessStatements"][2].update(status="complete"),
        ),
        "complete coverage cannot contain",
    )


def profile_payloads(document: dict[str, object]):
    for model in document.get("semanticModels", []):
        for fact in model.get("extensionFacts", []):
            if (fact.get("vocabulary"), fact.get("version")) == VOCABULARY:
                yield fact.get("payload")
        for summary in model.get("procedureSummaries", []):
            for transfer in summary.get("transfers", []):
                for extension in transfer.get("extensions", []):
                    if (extension.get("vocabulary"), extension.get("version")) == VOCABULARY:
                        yield extension.get("payload")


def main() -> int:
    core_schema = load(CORE_SCHEMA)
    profile_schema = load(PROFILE_SCHEMA)
    Draft202012Validator.check_schema(profile_schema)
    core = Draft202012Validator(core_schema, format_checker=FormatChecker())
    profile = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    failures: list[str] = []
    valid_documents: list[dict[str, object]] = []

    for path in sorted((PROFILE / "fixtures" / "valid").glob("*.json")):
        value = load(path)
        if isinstance(value, dict) and value.get("kind") is not None:
            errors = list(profile.iter_errors(value))
            if errors:
                failures.append(f"{path}: profile rejected valid payload: {errors[0].message}")
            continue
        core_errors = list(core.iter_errors(value))
        if core_errors:
            failures.append(f"{path}: core rejected valid fixture: {core_errors[0].message}")
            continue
        assert isinstance(value, dict)
        valid_documents.append(value)
        for payload in profile_payloads(value):
            errors = list(profile.iter_errors(payload))
            if errors:
                failures.append(f"{path}: profile rejected valid payload: {errors[0].message}")
        failures.extend(f"{path}: {issue}" for issue in semantic_issues(value))

    for path in sorted((PROFILE / "fixtures" / "invalid").glob("*.json")):
        if not list(profile.iter_errors(load(path))):
            failures.append(f"{path}: invalid fixture unexpectedly passed")

    if valid_documents:
        try:
            validator_contract_tests(valid_documents[0])
        except (AssertionError, KeyError, IndexError) as error:
            failures.append(f"validator contract test failed: {error}")
    else:
        failures.append("no valid value-transfer document fixture found")

    if failures:
        for failure in failures:
            print(f"FAIL: {failure}", file=sys.stderr)
        return 1
    print("value-transfer profile: schema, fixtures, attachments, and semantics passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
