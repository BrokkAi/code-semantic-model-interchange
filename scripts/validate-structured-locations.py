#!/usr/bin/env python3
"""Validate structured-location projections and their CSMI joins."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
CORE_SCHEMA = ROOT / "spec" / "0.1" / "schema.json"
PROFILE = ROOT / "profiles" / "structured-locations" / "0.1"
PROFILE_SCHEMA = PROFILE / "schema.json"
PROFILE_SCHEMA_ID = "https://csmi.brokk.ai/schema/profiles/structured-locations/0.1/schema.json"
VOCABULARY = ("csmi.structured-locations", "0.1.0")
CORE_SLOT = "procedure-summary-projection"


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def profile_projections(model: dict[str, object]):
    for summary_index, summary in enumerate(model.get("procedureSummaries", [])):
        callable_id = summary.get("callable")
        for transfer_index, transfer in enumerate(summary.get("transfers", [])):
            for endpoint_name in ("source", "destination"):
                endpoint = transfer.get(endpoint_name, {})
                projection = endpoint.get("projection", {})
                if (
                    projection.get("scheme"),
                    projection.get("schemeVersion"),
                ) == VOCABULARY:
                    yield (
                        callable_id,
                        endpoint,
                        projection,
                        transfer.get("provenance"),
                        f"procedureSummaries[{summary_index}].transfers[{transfer_index}].{endpoint_name}",
                    )


def semantic_issues(document: object) -> list[str]:
    issues: list[str] = []
    if not isinstance(document, dict):
        return ["document is not an object"]
    provenance_ids = {
        record.get("id") for record in document.get("provenanceRecords", [])
        if isinstance(record, dict)
    }
    default_provenance = document.get("defaultProvenance")
    for model_index, raw_model in enumerate(document.get("semanticModels", [])):
        if not isinstance(raw_model, dict):
            continue
        model = raw_model
        prefix = f"semanticModels[{model_index}]"
        declarations = {
            value.get("symbol"): value for value in model.get("declarations", [])
            if isinstance(value, dict)
        }
        symbols = {
            value.get("id"): value for value in model.get("symbols", [])
            if isinstance(value, dict)
        }
        uses = [
            value for value in model.get("vocabularyUses", [])
            if isinstance(value, dict)
            and (value.get("identifier"), value.get("version")) == VOCABULARY
        ]
        projections = list(profile_projections(model))
        if not (uses or projections):
            continue
        if len(uses) != 1:
            issues.append(f"{prefix}: requires exactly one structured-locations vocabulary use")
            affected: set[str] = set()
        else:
            use = uses[0]
            if use.get("schema") != PROFILE_SCHEMA_ID or use.get("requirement") != "required":
                issues.append(f"{prefix}: structured-locations use must name the exact schema and be required")
            affected = {
                canonical(unit.get("target")) for unit in use.get("affects", [])
                if isinstance(unit, dict)
                and unit.get("kind") == "core-slot"
                and unit.get("slot") == CORE_SLOT
            }
        for callable_id, endpoint, projection, transfer_provenance, path in projections:
            full_path = f"{prefix}.{path}"
            if canonical({"callable": callable_id}) not in affected:
                issues.append(f"{full_path}: callable projection target is absent from vocabulary affects")
            if declarations.get(callable_id, {}).get("category") != "callable":
                issues.append(f"{full_path}: enclosing callable must resolve locally")
            summary_tail_positions: list[int] = []
            any_positions: list[int] = []
            for step_index, step in enumerate(projection.get("steps", [])):
                step_path = f"{full_path}.projection.steps[{step_index}]"
                kind = step.get("kind")
                args = step.get("args", {})
                if kind in {"key", "index"}:
                    selector = args.get("selector", {})
                    selector_kind = selector.get("kind")
                    if selector_kind == "any":
                        any_positions.append(step_index)
                    elif selector_kind == "parameter":
                        position = selector.get("position")
                        declaration = declarations.get(callable_id, {})
                        parameters = declaration.get("callable", {}).get("parameters", [])
                        if not any(parameter.get("position") == position for parameter in parameters):
                            issues.append(f"{step_path}: parameter selector is absent from callable shape")
                    elif selector_kind == "capture":
                        capture = declarations.get(selector.get("symbol"), {})
                        if capture.get("category") != "value":
                            issues.append(f"{step_path}: capture selector must resolve to a local value declaration")
                elif kind in {"field", "variant-payload"}:
                    symbol = args.get("symbol") if kind == "field" else args.get("variant")
                    declaration = declarations.get(symbol, {})
                    if declaration.get("category") != "value":
                        issues.append(f"{step_path}: {kind} symbol must resolve to a local value declaration")
                    identity = symbols.get(symbol, {})
                    if not identity or identity.get("stability") not in {"portable", "artifact-local"}:
                        issues.append(f"{step_path}: {kind} symbol lacks stable CSMI identity")
                elif kind == "summary-tail":
                    summary_tail_positions.append(step_index)
            if summary_tail_positions and summary_tail_positions != [len(projection.get("steps", [])) - 1]:
                issues.append(f"{full_path}: summary-tail must be the single final step")
            if any_positions and any_positions != [len(projection.get("steps", [])) - 1]:
                issues.append(f"{full_path}: any selector must be the single final step")
            provenance = transfer_provenance or default_provenance
            if isinstance(provenance, list):
                references = provenance
            elif provenance is None:
                references = []
            else:
                references = [provenance]
            if not references or any(reference not in provenance_ids for reference in references):
                issues.append(f"{full_path}: projection-bearing transfer lacks resolvable provenance")
    return issues


def expect_issue(document: dict[str, object], edit, expected: str) -> None:
    candidate = copy.deepcopy(document)
    edit(candidate)
    issues = semantic_issues(candidate)
    if not any(expected in issue for issue in issues):
        raise AssertionError(f"expected semantic issue containing {expected!r}, got {issues!r}")


def contract_tests(valid: dict[str, object]) -> None:
    model = lambda document: document["semanticModels"][0]
    projection = lambda document: model(document)["procedureSummaries"][1]["transfers"][0]["destination"]["projection"]
    expect_issue(
        valid,
        lambda document: model(document)["vocabularyUses"][0].update(requirement="optional"),
        "must name the exact schema and be required",
    )
    expect_issue(
        valid,
        lambda document: model(document)["vocabularyUses"][0]["affects"][0].update(target={"callable": "other"}),
        "target is absent",
    )
    expect_issue(
        valid,
        lambda document: model(document)["procedureSummaries"][0]["transfers"][0]["destination"]["projection"]["steps"][0]["args"]["selector"].update(position=9),
        "absent from callable shape",
    )
    expect_issue(
        valid,
        lambda document: projection(document)["steps"].insert(0, {"kind": "summary-tail", "args": {"causes": ["path-limit"]}}),
        "summary-tail must be the single final step",
    )
    expect_issue(
        valid,
        lambda document: document.update(defaultProvenance="missing"),
        "lacks resolvable provenance",
    )


def main() -> int:
    profile_schema = load(PROFILE_SCHEMA)
    profile_validator = Draft202012Validator(profile_schema, format_checker=FormatChecker())
    core_validator = Draft202012Validator(load(CORE_SCHEMA), format_checker=FormatChecker())
    failures = 0
    counts = {"valid": 0, "invalid": 0, "semantic-invalid": 0}
    for group, structurally_valid, semantically_valid in (
        ("valid", True, True),
        ("invalid", False, False),
        ("semantic-invalid", True, False),
    ):
        fixtures = sorted((PROFILE / "fixtures" / group).glob("*.json"))
        if not fixtures:
            failures += 1
            print(f"{PROFILE / 'fixtures' / group}: no fixtures", file=sys.stderr)
        counts[group] = len(fixtures)
        for fixture in fixtures:
            value = load(fixture)
            errors = list(profile_validator.iter_errors(value))
            if structurally_valid != (not errors):
                failures += 1
                print(f"{fixture.relative_to(ROOT)}: unexpected structural outcome", file=sys.stderr)
            if group == "semantic-invalid" and not errors:
                steps = value.get("steps", []) if isinstance(value, dict) else []
                tails = [index for index, step in enumerate(steps) if step.get("kind") == "summary-tail"]
                any_before_end = any(
                    step.get("kind") in {"key", "index"}
                    and step.get("args", {}).get("selector", {}).get("kind") == "any"
                    and index != len(steps) - 1
                    for index, step in enumerate(steps)
                )
                if not any_before_end and not (tails and tails != [len(steps) - 1]):
                    failures += 1
                    print(f"{fixture.relative_to(ROOT)}: expected semantic violation", file=sys.stderr)
    documents = sorted((PROFILE / "fixtures" / "valid-documents").glob("*.json"))
    if not documents:
        failures += 1
        print("no valid structured-location document fixture", file=sys.stderr)
    for path in documents:
        document = load(path)
        core_errors = list(core_validator.iter_errors(document))
        profile_errors = [
            error for _, _, projection, _, _ in profile_projections(document["semanticModels"][0])
            for error in profile_validator.iter_errors(projection)
        ]
        issues = semantic_issues(document)
        if core_errors or profile_errors or issues:
            failures += 1
            print(f"{path.relative_to(ROOT)}: {core_errors or profile_errors or issues}", file=sys.stderr)
        else:
            contract_tests(document)
    if failures:
        return 1
    print(
        "structured locations: "
        f"{counts['valid']} payload positives, {counts['invalid']} structural rejections, "
        f"{counts['semantic-invalid']} semantic rejections, and {len(documents)} documents passed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
