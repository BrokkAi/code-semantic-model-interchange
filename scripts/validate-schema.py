#!/usr/bin/env python3
"""Meta-validate the CSMI schema and check every fixture expectation."""

from __future__ import annotations

import base64
import hashlib
import json
import sys
from pathlib import Path
from typing import Iterable

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, ValidationError, best_match


ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "spec" / "0.1" / "schema.json"
PROFILE_SCHEMAS = {
    "https://csmi.brokk.ai/schema/profiles/javascript-typescript/0.1/schema.json":
        ROOT / "profiles" / "javascript-typescript" / "0.1" / "schema.json",
    "https://csmi.brokk.ai/schema/profiles/node-compatibility/0.1/schema.json":
        ROOT / "profiles" / "node-compatibility" / "0.1" / "schema.json",
    "https://csmi.brokk.ai/schema/profiles/value-transfer/0.1/schema.json":
        ROOT / "profiles" / "value-transfer" / "0.1" / "schema.json",
    "https://csmi.brokk.ai/schema/profiles/cpp/0.1/schema.json":
        ROOT / "profiles" / "cpp" / "0.1" / "schema.json",
}
PROFILE_REQUIRED_USES = {
    ("csmi.javascript-typescript", "0.1.0"),
    ("csmi.node-compatibility", "0.1.0"),
    ("csmi.value-transfer", "0.1.0"),
    ("csmi.cpp", "0.1.0"),
    ("csmi.c-cpp-resolution", "0.1.0"),
}
PROFILE_VOCABULARIES = {
    ("csmi.javascript-typescript", "0.1.0"):
        "https://csmi.brokk.ai/schema/profiles/javascript-typescript/0.1/schema.json",
    ("csmi.node-compatibility", "0.1.0"):
        "https://csmi.brokk.ai/schema/profiles/node-compatibility/0.1/schema.json",
    ("csmi.value-transfer", "0.1.0"):
        "https://csmi.brokk.ai/schema/profiles/value-transfer/0.1/schema.json",
    ("csmi.cpp", "0.1.0"):
        "https://csmi.brokk.ai/schema/profiles/cpp/0.1/schema.json",
    ("csmi.c-cpp-resolution", "0.1.0"):
        "https://csmi.brokk.ai/schema/profiles/cpp/0.1/schema.json",
}
FIXTURE_GROUPS = {
    "valid": True,
    "invalid": False,
    "semantic-invalid": True,
}


def iter_profile_instances(value: object) -> Iterable[tuple[str, object, str]]:
    """Yield known profile payloads from a structurally valid CSMI document."""
    if not isinstance(value, dict):
        return
    for model_index, model in enumerate(value.get("semanticModels", [])):
        for constraint_index, constraint in enumerate(model.get("compatibilityConstraints", [])):
            schema_uri = PROFILE_VOCABULARIES.get(
                (constraint.get("vocabulary"), constraint.get("version"))
            )
            if schema_uri in PROFILE_SCHEMAS:
                yield schema_uri, constraint.get("value"), (
                    f"$.semanticModels[{model_index}]"
                    f".compatibilityConstraints[{constraint_index}].value"
                )
        for fact_index, fact in enumerate(model.get("extensionFacts", [])):
            schema_uri = PROFILE_VOCABULARIES.get(
                (fact.get("vocabulary"), fact.get("version"))
            )
            if schema_uri in PROFILE_SCHEMAS:
                yield schema_uri, fact.get("payload"), (
                    f"$.semanticModels[{model_index}].extensionFacts[{fact_index}].payload"
                )
        for symbol_index, symbol in enumerate(model.get("symbols", [])):
            for extension_index, extension in enumerate(symbol.get("extensions", [])):
                schema_uri = PROFILE_VOCABULARIES.get(
                    (extension.get("vocabulary"), extension.get("version"))
                )
                if schema_uri in PROFILE_SCHEMAS:
                    yield schema_uri, extension.get("payload"), (
                        f"$.semanticModels[{model_index}].symbols[{symbol_index}]"
                        f".extensions[{extension_index}].payload"
                    )
        for summary_index, summary in enumerate(model.get("procedureSummaries", [])):
            for transfer_index, transfer in enumerate(summary.get("transfers", [])):
                for extension_index, extension in enumerate(transfer.get("extensions", [])):
                    schema_uri = PROFILE_VOCABULARIES.get(
                        (extension.get("vocabulary"), extension.get("version"))
                    )
                    if schema_uri in PROFILE_SCHEMAS:
                        yield schema_uri, extension.get("payload"), (
                            f"$.semanticModels[{model_index}]"
                            f".procedureSummaries[{summary_index}].transfers[{transfer_index}]"
                            f".extensions[{extension_index}].payload"
                        )


def semantic_errors(value: object) -> list[str]:
    """Check repository-owned profile invariants beyond JSON Schema."""
    errors: list[str] = []
    if not isinstance(value, dict):
        return errors
    for model_index, model in enumerate(value.get("semanticModels", [])):
        declared_uses = {
            (use.get("identifier"), use.get("version")): use
            for use in model.get("vocabularyUses", [])
            if isinstance(use, dict)
        }
        symbols = {
            symbol.get("id"): symbol
            for symbol in model.get("symbols", [])
            if isinstance(symbol, dict)
        }
        node_distribution_selectors = [
            selector
            for selector in model.get("artifactSelectors", [])
            if isinstance(selector, dict)
            and selector.get("purl", "").startswith("pkg:generic/nodejs.org/node@")
        ]
        for selector in node_distribution_selectors:
            if not any(
                digest.get("coverage") == "official-distribution-archive"
                for digest in selector.get("digests", [])
                if isinstance(digest, dict)
            ):
                errors.append(
                    f"$.semanticModels[{model_index}].artifactSelectors: "
                    "a Node distribution selector requires an official-distribution-archive digest"
                )
        for use_index, use in enumerate(model.get("vocabularyUses", [])):
            key = (use.get("identifier"), use.get("version"))
            if key in PROFILE_REQUIRED_USES and use.get("requirement") != "required":
                errors.append(
                    f"$.semanticModels[{model_index}].vocabularyUses[{use_index}]: "
                    f"{key[0]} {key[1]} affects identity or compatibility and must be required"
                )
            expected_schema = PROFILE_VOCABULARIES.get(key)
            if expected_schema is not None and use.get("schema") != expected_schema:
                errors.append(
                    f"$.semanticModels[{model_index}].vocabularyUses[{use_index}]: "
                    f"{key[0]} {key[1]} must declare its exact standard schema"
                )
        identity_use = declared_uses.get(("csmi.javascript-typescript", "0.1.0"))
        cpp_identity_use = declared_uses.get(("csmi.cpp", "0.1.0"))
        for symbol_index, symbol in enumerate(model.get("symbols", [])):
            scheme = symbol.get("scheme")
            if scheme == "csmi.cpp.declaration" and cpp_identity_use is None:
                errors.append(
                    f"$.semanticModels[{model_index}].symbols[{symbol_index}]: "
                    "C++ profile identity scheme requires an exact vocabulary use"
                )
            if scheme in {"csmi.javascript-runtime", "csmi.typescript-declaration"}:
                if identity_use is None:
                    errors.append(
                        f"$.semanticModels[{model_index}].symbols[{symbol_index}]: "
                        "profile identity scheme requires an exact vocabulary use"
                    )
                descriptors = symbol.get("descriptors", [])
                if not descriptors or descriptors[0].get("role") != "namespace":
                    errors.append(
                        f"$.semanticModels[{model_index}].symbols[{symbol_index}].descriptors: "
                        "profile identity must begin with a namespace descriptor"
                    )
                if (
                    len(descriptors) > 2
                    and descriptors[1].get("role") == "type"
                    and (
                        descriptors[2].get("role") != "meta"
                        or descriptors[2].get("name") not in {"static", "prototype"}
                    )
                ):
                    errors.append(
                        f"$.semanticModels[{model_index}].symbols[{symbol_index}].descriptors[2]: "
                        "a nested type member requires a static or prototype receiver descriptor"
                    )
            for extension_index, extension in enumerate(symbol.get("extensions", [])):
                key = (extension.get("vocabulary"), extension.get("version"))
                if key in PROFILE_VOCABULARIES and key not in declared_uses:
                    errors.append(
                        f"$.semanticModels[{model_index}].symbols[{symbol_index}]"
                        f".extensions[{extension_index}]: profile payload requires "
                        "an exact vocabulary use"
                    )
                payload = extension.get("payload", {})
                if (
                    key == ("csmi.javascript-typescript", "0.1.0")
                    and payload.get("kind") == "module-binding"
                ):
                    descriptors = symbol.get("descriptors", [])
                    canonical_module = descriptors[0].get("name") if descriptors else None
                    export_name = descriptors[1].get("name") if len(descriptors) > 1 else None
                    if payload.get("canonicalModule") != canonical_module:
                        errors.append(
                            f"$.semanticModels[{model_index}].symbols[{symbol_index}]"
                            f".extensions[{extension_index}].payload.canonicalModule: "
                            "must equal the identity's namespace descriptor"
                        )
                    if payload.get("exportName") != export_name:
                        errors.append(
                            f"$.semanticModels[{model_index}].symbols[{symbol_index}]"
                            f".extensions[{extension_index}].payload.exportName: "
                            "must equal the identity's first exported descriptor"
                        )
        for fact_index, fact in enumerate(model.get("extensionFacts", [])):
            fact_key = (fact.get("vocabulary"), fact.get("version"))
            if fact_key in PROFILE_VOCABULARIES and fact_key not in declared_uses:
                errors.append(
                    f"$.semanticModels[{model_index}].extensionFacts[{fact_index}]: "
                    "profile payload requires an exact vocabulary use"
                )
            if (
                fact.get("vocabulary") == "csmi.javascript-typescript"
                and fact.get("version") == "0.1.0"
                and fact.get("family") == "runtime-declaration-bindings"
            ):
                payload = fact.get("payload", {})
                if fact.get("scope", {}).get("runtimeSymbol") != payload.get("runtimeSymbol"):
                    errors.append(
                        f"$.semanticModels[{model_index}].extensionFacts[{fact_index}]: "
                        "scope.runtimeSymbol must equal payload.runtimeSymbol"
                    )
                runtime = symbols.get(payload.get("runtimeSymbol"), {})
                declarations = [
                    symbols.get(handle, {})
                    for handle in payload.get("declarationSymbols", [])
                ]
                if runtime.get("scheme") != "csmi.javascript-runtime":
                    errors.append(
                        f"$.semanticModels[{model_index}].extensionFacts[{fact_index}]: "
                        "runtimeSymbol must use csmi.javascript-runtime"
                    )
                if any(
                    declaration.get("scheme") != "csmi.typescript-declaration"
                    for declaration in declarations
                ):
                    errors.append(
                        f"$.semanticModels[{model_index}].extensionFacts[{fact_index}]: "
                        "every declarationSymbol must use csmi.typescript-declaration"
                    )
        for constraint_index, constraint in enumerate(model.get("compatibilityConstraints", [])):
            constraint_key = (constraint.get("vocabulary"), constraint.get("version"))
            if constraint_key in PROFILE_VOCABULARIES and constraint_key not in declared_uses:
                errors.append(
                    f"$.semanticModels[{model_index}]"
                    f".compatibilityConstraints[{constraint_index}]: "
                    "profile value requires an exact vocabulary use"
                )
            value = constraint.get("value", {})
            if (
                constraint_key == ("csmi.node-compatibility", "0.1.0")
                and value.get("kind") == "node-module-resolution"
            ):
                conditions = set(value.get("conditions", []))
                if "import" in conditions and "require" in conditions:
                    errors.append(
                        f"$.semanticModels[{model_index}]"
                        f".compatibilityConstraints[{constraint_index}].value.conditions: "
                        "import and require are mutually exclusive"
                    )
                if (
                    value.get("moduleSystem") == "esm" and "require" in conditions
                ) or (
                    value.get("moduleSystem") == "commonjs" and "import" in conditions
                ):
                    errors.append(
                        f"$.semanticModels[{model_index}]"
                        f".compatibilityConstraints[{constraint_index}].value.conditions: "
                        "module condition contradicts moduleSystem"
                    )
            if (
                constraint.get("vocabulary") == "csmi.node-compatibility"
                and constraint.get("version") == "0.1.0"
                and value.get("kind") in {"node-runtime", "typescript-resolution"}
            ):
                interval_key = (
                    "versionInterval"
                    if value.get("kind") == "node-runtime"
                    else "compilerVersionInterval"
                )
                interval = value.get(interval_key, {})
                lower = interval.get("minimum")
                upper = interval.get("maximum")
                if lower and upper:
                    lower_version = semver_precedence(lower.get("version", ""))
                    upper_version = semver_precedence(upper.get("version", ""))
                    if lower_version is not None and upper_version is not None:
                        if lower_version > upper_version or (
                            lower_version == upper_version
                            and (not lower.get("inclusive") or not upper.get("inclusive"))
                        ):
                            errors.append(
                                f"$.semanticModels[{model_index}]"
                                f".compatibilityConstraints[{constraint_index}].value"
                                f".{interval_key}: interval is empty"
                            )
    return errors


def semver_precedence(value: str) -> tuple[int, int, int, tuple[tuple[int, object], ...]] | None:
    """Parse the schema-validated SemVer subset for interval ordering."""
    import re

    match = re.fullmatch(
        r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
        r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
        r"(?:\+[0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*)?",
        value,
    )
    if not match:
        return None
    prerelease = match.group(4)
    if prerelease is None:
        encoded = ((2, ""),)
    else:
        parts: list[tuple[int, object]] = []
        for part in prerelease.split("."):
            if part.isdigit():
                parts.append((0, int(part)))
            else:
                parts.append((1, part))
        encoded = tuple(parts)
    return int(match.group(1)), int(match.group(2)), int(match.group(3)), encoded


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


def canonical_signature_bytes(value: object) -> bytes:
    """Canonicalize the ASCII/integer signature-fixture subset exactly as JCS."""

    def check(item: object) -> None:
        if isinstance(item, float):
            raise ValueError("floating-point values are outside the signature-fixture subset")
        if isinstance(item, str) and not item.isascii():
            raise ValueError("non-ASCII strings are outside the signature-fixture subset")
        if isinstance(item, dict):
            for key, child in item.items():
                check(key)
                check(child)
        elif isinstance(item, list):
            for child in item:
                check(child)

    check(value)
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def validate_signature_fixtures() -> tuple[int, list[str]]:
    """Recompute each tsig digest and bind it to a serialized fixture symbol."""
    manifest_path = ROOT / "fixtures" / "profile-inputs" / "typescript-signatures.json"
    manifest = load_json(manifest_path)
    records = manifest.get("records", []) if isinstance(manifest, dict) else []
    errors: list[str] = []
    if not records:
        errors.append(f"{manifest_path.relative_to(ROOT)}: no signature records found")
    for index, record in enumerate(records):
        if not isinstance(record, dict):
            errors.append(f"{manifest_path.relative_to(ROOT)}.records[{index}]: expected object")
            continue
        canonical_input = record.get("canonicalInput")
        if not isinstance(canonical_input, dict) or canonical_input.get("callableKind") not in {
            "call", "construct", "getter", "setter"
        }:
            errors.append(
                f"{manifest_path.relative_to(ROOT)}.records[{index}]: "
                "canonicalInput requires a recognized callableKind"
            )
            continue
        try:
            digest = base64.urlsafe_b64encode(
                hashlib.sha256(canonical_signature_bytes(canonical_input)).digest()
            ).rstrip(b"=").decode("ascii")
            fixture = load_json(ROOT / "fixtures" / record["fixture"])
        except (KeyError, OSError, ValueError) as error:
            errors.append(f"{manifest_path.relative_to(ROOT)}.records[{index}]: {error}")
            continue
        matches = [
            symbol
            for model in fixture.get("semanticModels", [])
            for symbol in model.get("symbols", [])
            if symbol.get("id") == record.get("symbol")
        ]
        expected = f"tsig-0.1:{digest}"
        if len(matches) != 1 or not any(
            descriptor.get("disambiguator") == expected
            for descriptor in matches[0].get("descriptors", [])
        ):
            errors.append(
                f"{manifest_path.relative_to(ROOT)}.records[{index}]: "
                f"fixture symbol does not carry recomputed {expected}"
            )
    return len(records), errors


def main() -> int:
    schema = load_json(SCHEMA_PATH)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        print(f"{SCHEMA_PATH.relative_to(ROOT)}: invalid schema: {error.message}", file=sys.stderr)
        return 1

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    profile_validators: dict[str, Draft202012Validator] = {}
    for schema_uri, profile_path in PROFILE_SCHEMAS.items():
        profile_schema = load_json(profile_path)
        try:
            Draft202012Validator.check_schema(profile_schema)
        except SchemaError as error:
            print(
                f"{profile_path.relative_to(ROOT)}: invalid schema: {error.message}",
                file=sys.stderr,
            )
            return 1
        if profile_schema.get("$id") != schema_uri:
            print(
                f"{profile_path.relative_to(ROOT)}: $id does not match {schema_uri}",
                file=sys.stderr,
            )
            return 1
        profile_validators[schema_uri] = Draft202012Validator(
            profile_schema,
            format_checker=FormatChecker(),
        )
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
            elif should_validate and not errors:
                for schema_uri, profile_instance, location in iter_profile_instances(instance):
                    profile_errors = list(
                        profile_validators[schema_uri].iter_errors(profile_instance)
                    )
                    if profile_errors:
                        failures += 1
                        print(
                            f"{path.relative_to(ROOT)}: expected profile payload validity at "
                            f"{location}; {describe_error(profile_errors)}",
                            file=sys.stderr,
                        )
                semantic_profile_errors = semantic_errors(instance)
                if group == "valid" and semantic_profile_errors:
                    failures += len(semantic_profile_errors)
                    for message in semantic_profile_errors:
                        print(f"{path.relative_to(ROOT)}: {message}", file=sys.stderr)
                elif group == "semantic-invalid":
                    is_profile_semantic_fixture = path.name.startswith(
                        ("javascript-", "node-")
                    )
                    if is_profile_semantic_fixture and not semantic_profile_errors:
                        failures += 1
                        print(
                            f"{path.relative_to(ROOT)}: expected a profile semantic violation",
                            file=sys.stderr,
                        )

    signature_count, signature_errors = validate_signature_fixtures()
    failures += len(signature_errors)
    for message in signature_errors:
        print(message, file=sys.stderr)

    if failures:
        print(f"Schema validation failed for {failures} expectation(s)", file=sys.stderr)
        return 1

    print(
        "Schema validation passed: "
        f"{counts['valid']} valid, "
        f"{counts['invalid']} structurally rejected, "
        f"{counts['semantic-invalid']} semantic-invalid structurally accepted, "
        f"{len(profile_validators)} profile schemas, "
        f"{signature_count} TypeScript signature digest verified"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
