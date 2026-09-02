#!/usr/bin/env python3
"""Meta-validate every versioned profile schema and its fixture expectations."""

from __future__ import annotations

import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, best_match


ROOT = Path(__file__).resolve().parents[1]


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    failures = 0
    schemas = sorted(ROOT.glob("profiles/*/*/schema.json"))
    if not schemas:
        print("No profile schemas found", file=sys.stderr)
        return 1

    counts = {"schemas": len(schemas), "valid": 0, "invalid": 0}
    for schema_path in schemas:
        schema = load_json(schema_path)
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            failures += 1
            print(f"{schema_path.relative_to(ROOT)}: invalid schema: {error.message}", file=sys.stderr)
            continue

        validator = Draft202012Validator(schema, format_checker=FormatChecker())
        for group, should_validate in (("valid", True), ("invalid", False)):
            fixture_dir = schema_path.parent / "fixtures" / group
            fixtures = sorted(fixture_dir.glob("*.json"))
            if not fixtures:
                failures += 1
                print(f"{fixture_dir.relative_to(ROOT)}: no JSON fixtures found", file=sys.stderr)
                continue
            counts[group] += len(fixtures)
            for fixture_path in fixtures:
                instance = load_json(fixture_path)
                errors = list(validator.iter_errors(instance))
                if should_validate and errors:
                    failures += 1
                    error = best_match(errors)
                    message = error.message if error else "unknown validation error"
                    print(f"{fixture_path.relative_to(ROOT)}: expected validity: {message}", file=sys.stderr)
                elif not should_validate and not errors:
                    failures += 1
                    print(f"{fixture_path.relative_to(ROOT)}: expected schema rejection", file=sys.stderr)

        if schema_path.relative_to(ROOT).as_posix() == "profiles/python/0.1/schema.json":
            for document_path in sorted((ROOT / "fixtures" / "valid").glob("*.json")):
                document = load_json(document_path)
                if not isinstance(document, dict):
                    continue
                if document.get("documentType") != "semantic-document":
                    continue
                for model_index, model in enumerate(document.get("semanticModels", [])):
                    for constraint_index, constraint in enumerate(model.get("compatibilityConstraints", [])):
                        if constraint.get("vocabulary") != "csmi.python":
                            continue
                        errors = list(validator.iter_errors(constraint.get("value")))
                        if errors:
                            failures += 1
                            error = best_match(errors)
                            message = error.message if error else "unknown validation error"
                            print(
                                f"{document_path.relative_to(ROOT)}: semanticModels[{model_index}]"
                                f".compatibilityConstraints[{constraint_index}].value: {message}",
                                file=sys.stderr,
                            )
                    for fact_index, fact in enumerate(model.get("extensionFacts", [])):
                        if fact.get("vocabulary") != "csmi.python":
                            continue
                        payload = fact.get("payload")
                        errors = list(validator.iter_errors(payload))
                        if not errors and isinstance(payload, dict) and payload.get("kind") != fact.get("family"):
                            failures += 1
                            print(
                                f"{document_path.relative_to(ROOT)}: semanticModels[{model_index}]"
                                f".extensionFacts[{fact_index}]: family and payload kind differ",
                                file=sys.stderr,
                            )
                        elif errors:
                            failures += 1
                            error = best_match(errors)
                            message = error.message if error else "unknown validation error"
                            print(
                                f"{document_path.relative_to(ROOT)}: semanticModels[{model_index}]"
                                f".extensionFacts[{fact_index}].payload: {message}",
                                file=sys.stderr,
                            )

    if failures:
        print(f"Profile validation failed for {failures} expectation(s)", file=sys.stderr)
        return 1
    print(
        "Profile validation passed: "
        f"{counts['schemas']} schema, {counts['valid']} valid, "
        f"{counts['invalid']} structurally rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
