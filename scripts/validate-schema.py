#!/usr/bin/env python3
"""Meta-validate the CSMI schema and check every fixture expectation."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError, best_match


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "0.1" / "schema.json"
FIXTURE_GROUPS = {
    "valid": True,
    "invalid": False,
    "semantic-invalid": True,
}


def load_json(path: Path) -> object:
    with path.open(encoding="utf-8") as source:
        return json.load(source)


def fixture_paths(group: str) -> list[Path]:
    return sorted((ROOT / "fixtures" / group).glob("*.json"))


def json_path(parts: Iterable[object]) -> str:
    result = "$"
    for part in parts:
        if isinstance(part, int):
            result += f"[{part}]"
        else:
            result += f".{part}"
    return result


def describe_error(errors: list[ValidationError]) -> str:
    error = best_match(errors)
    if error is None:
        return "unknown validation error"
    return f"{json_path(error.absolute_path)}: {error.message}"


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        print(f"{SCHEMA_PATH.relative_to(ROOT)}: invalid schema: {error.message}", file=sys.stderr)
        return 1

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    failures = 0
    counts: dict[str, int] = {}

    for group, should_validate in FIXTURE_GROUPS.items():
        paths = fixture_paths(group)
        counts[group] = len(paths)
        if not paths:
            failures += 1
            print(f"fixtures/{group}: no JSON fixtures found", file=sys.stderr)
            continue

        for path in paths:
            instance = load_json(path)
            errors = list(validator.iter_errors(instance))
            if should_validate and errors:
                failures += 1
                print(
                    f"{path.relative_to(ROOT)}: expected structural validity; "
                    f"{describe_error(errors)}",
                    file=sys.stderr,
                )
            elif not should_validate and not errors:
                failures += 1
                print(
                    f"{path.relative_to(ROOT)}: expected schema rejection but validated",
                    file=sys.stderr,
                )

    if failures:
        print(f"Schema validation failed for {failures} expectation(s)", file=sys.stderr)
        return 1

    print(
        "Schema validation passed: "
        f"{counts['valid']} valid, "
        f"{counts['invalid']} structurally rejected, "
        f"{counts['semantic-invalid']} semantic-invalid structurally accepted"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
