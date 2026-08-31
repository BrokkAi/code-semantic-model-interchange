#!/usr/bin/env python3
"""Parse repository JSON strictly using only the Python standard library."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from decimal import Decimal
from pathlib import Path
from typing import NoReturn


ROOT = Path(__file__).resolve().parents[1]


class DuplicateKeyError(ValueError):
    pass


def reject_constant(value: str) -> NoReturn:
    raise ValueError(f"non-finite JSON number {value!r}")


def unique_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    result: dict[str, object] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate object key {key!r}")
        result[key] = value
    return result


def validate_unicode(value: object, location: str = "$") -> None:
    if isinstance(value, str):
        for character in value:
            code_point = ord(character)
            if 0xD800 <= code_point <= 0xDFFF:
                raise ValueError(f"lone Unicode surrogate at {location}")
        return
    if isinstance(value, list):
        for index, item in enumerate(value):
            validate_unicode(item, f"{location}[{index}]")
        return
    if isinstance(value, dict):
        for key, item in value.items():
            validate_unicode(key, f"{location}.<key>")
            validate_unicode(item, f"{location}.{key}")
        return
    if isinstance(value, Decimal) and not value.is_finite():
        raise ValueError(f"non-finite JSON number at {location}")


def repository_json_files() -> list[Path]:
    completed = subprocess.run(
        [
            "git",
            "ls-files",
            "--cached",
            "--others",
            "--exclude-standard",
            "-z",
            "--",
            "*.json",
        ],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(
        ROOT / os.fsdecode(path)
        for path in completed.stdout.split(b"\0")
        if path
    )


def lint(path: Path) -> None:
    source = path.read_text(encoding="utf-8")
    parsed = json.loads(
        source,
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
        parse_float=Decimal,
    )
    validate_unicode(parsed)


def main() -> int:
    paths = repository_json_files()
    if not paths:
        print("No JSON files found", file=sys.stderr)
        return 1

    failures = 0
    for path in paths:
        try:
            lint(path)
        except (OSError, UnicodeError, ValueError, json.JSONDecodeError) as error:
            failures += 1
            print(f"{path.relative_to(ROOT)}: {error}", file=sys.stderr)

    if failures:
        print(f"JSON lint failed for {failures} file(s)", file=sys.stderr)
        return 1

    print(f"JSON lint passed for {len(paths)} file(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
