#!/usr/bin/env python3
"""Validate CSMI C/C++ profile shape, canonical keys, and exact fixtures."""

from __future__ import annotations

import hashlib
import json
import sys
import unicodedata
from copy import deepcopy
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, best_match


ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = ROOT / "profiles" / "cpp" / "0.1"
SCHEMA_PATH = PROFILE_ROOT / "schema.json"
SIGNATURE_INPUTS = ROOT / "fixtures" / "profile-inputs" / "cpp-signatures.json"
RESOLUTION_INPUT = ROOT / "fixtures" / "profile-inputs" / "cpp-resolution.json"
RESOLUTION_FIXTURE = PROFILE_ROOT / "fixtures" / "valid" / "resolution-context.json"
COPY_FIXTURE = PROFILE_ROOT / "fixtures" / "valid" / "copy-constructor.json"
VALUE_TRANSFER_FIXTURE = (
    ROOT / "profiles" / "value-transfer" / "0.1" / "fixtures" / "valid" / "basic-string-copy.json"
)


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_bytes(value: object) -> bytes:
    """RFC 8785 serialization for this profile's integer-free JSON subset."""
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def disambiguator(value: object) -> str:
    return "cppsig-0.1:" + hashlib.sha256(canonical_bytes(value)).hexdigest()


def declared_owner(value: object, owner: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("kind") == "declared"
        and value.get("symbol") == owner
    )


def lvalue_owner(value: object, owner: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("kind") == "reference"
        and value.get("referenceKind") == "lvalue"
        and declared_owner(value.get("referent"), owner)
    )


def const_lvalue_owner(value: object, owner: object) -> bool:
    if not isinstance(value, dict):
        return False
    referent = value.get("referent")
    return (
        value.get("kind") == "reference"
        and value.get("referenceKind") == "lvalue"
        and isinstance(referent, dict)
        and referent.get("kind") == "qualified"
        and referent.get("qualifiers") == ["const"]
        and declared_owner(referent.get("type"), owner)
    )


def rvalue_owner(value: object, owner: object) -> bool:
    return (
        isinstance(value, dict)
        and value.get("kind") == "reference"
        and value.get("referenceKind") == "rvalue"
        and declared_owner(value.get("referent"), owner)
    )


def symbol_key_issues(key: object) -> list[str]:
    if not isinstance(key, dict):
        return ["symbol key is not an object"]
    issues: list[str] = []
    selectors = key.get("artifactSelectors", [])
    if not selectors or any(not selector.get("digests") for selector in selectors):
        issues.append("portable C++ symbol lacks exact-content artifact selectors")
    descriptors = key.get("descriptors", [])
    for descriptor in descriptors:
        name = descriptor.get("name", "")
        if name != unicodedata.normalize("NFC", name):
            issues.append("descriptor name is not NFC normalized")
        role = descriptor.get("role")
        kind = descriptor.get("disambiguator", "")
        if role == "namespace" and kind != "namespace":
            issues.append("namespace descriptor lacks namespace disambiguator")
        elif role == "type" and not (
            kind == "type-alias" or kind.startswith("template-primary:")
        ):
            issues.append("type descriptor has an unsupported identity form")
        elif role == "callable" and not kind.startswith("cppsig-0.1:"):
            issues.append("callable descriptor lacks cppsig-0.1 identity")
    return issues


def signature_issues(operation: object, signature: object) -> list[str]:
    if not isinstance(signature, dict):
        return ["signature is not an object"]
    owner = signature.get("owner")
    issues = symbol_key_issues(owner)
    if not exact_std_template(owner, "basic_string", 3):
        issues.append("special-member owner is not exact std::basic_string primary")
    parameters = signature.get("parameters", [])
    if operation == "copy-constructor":
        if len(parameters) != 1 or not const_lvalue_owner(parameters[0], owner):
            issues.append("copy constructor does not have one const lvalue self parameter")
        if signature.get("callableKind") != "constructor":
            issues.append("copy constructor has the wrong callable kind")
        if "receiver" in signature or "result" in signature:
            issues.append("copy constructor must not carry receiver or result")
    elif operation == "copy-assignment":
        if len(parameters) != 1 or not const_lvalue_owner(parameters[0], owner):
            issues.append("copy assignment does not have one const lvalue self parameter")
        if signature.get("callableKind") != "method":
            issues.append("copy assignment has the wrong callable kind")
        if not lvalue_owner(signature.get("receiver"), owner):
            issues.append("copy assignment receiver is not lvalue self")
        if not lvalue_owner(signature.get("result"), owner):
            issues.append("copy assignment result is not lvalue self")
    elif operation == "move-constructor":
        if len(parameters) != 1 or not rvalue_owner(parameters[0], owner):
            issues.append("move constructor does not have one rvalue self parameter")
        if signature.get("callableKind") != "constructor":
            issues.append("move constructor has the wrong callable kind")
        if "receiver" in signature or "result" in signature:
            issues.append("move constructor must not carry receiver or result")
    else:
        issues.append("unsupported implicit operation")
    return issues


def canonical_type_issues(value: object) -> list[str]:
    if not isinstance(value, dict):
        return ["canonical type is not an object"]
    kind = value.get("kind")
    if kind == "declared":
        return symbol_key_issues(value.get("symbol"))
    if kind == "template-specialization":
        issues = symbol_key_issues(value.get("primary"))
        for argument in value.get("arguments", []):
            issues.extend(canonical_type_issues(argument))
        return issues
    if kind == "qualified":
        qualifiers = value.get("qualifiers", [])
        issues = [] if qualifiers == sorted(qualifiers) else ["qualifiers are not canonical"]
        return issues + canonical_type_issues(value.get("type"))
    if kind == "reference":
        return canonical_type_issues(value.get("referent"))
    if kind == "fundamental" and value.get("name") == "char":
        return []
    return ["unsupported canonical type"]


def exact_std_template(key: object, name: str, arity: int) -> bool:
    if not isinstance(key, dict):
        return False
    descriptors = key.get("descriptors")
    return descriptors == [
        {"role": "namespace", "name": "std", "disambiguator": "namespace"},
        {
            "role": "type",
            "name": name,
            "disambiguator": f"template-primary:{arity}",
        },
    ]


def std_string_alias_issues(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["alias payload is not an object"]
    target = payload.get("target", {})
    issues = canonical_type_issues(target)
    arguments = target.get("arguments", []) if isinstance(target, dict) else []
    if (
        target.get("kind") != "template-specialization"
        or not exact_std_template(target.get("primary"), "basic_string", 3)
        or len(arguments) != 3
        or arguments[0] != {"kind": "fundamental", "name": "char"}
    ):
        return issues + ["alias is not the canonical std::string specialization"]
    for position, name in ((1, "char_traits"), (2, "allocator")):
        argument = arguments[position]
        if not (
            isinstance(argument, dict)
            and argument.get("kind") == "template-specialization"
            and exact_std_template(argument.get("primary"), name, 1)
            and argument.get("arguments") == [{"kind": "fundamental", "name": "char"}]
        ):
            issues.append(f"alias has a non-canonical {name}<char> argument")
    return issues


def validate_profile_fixtures(validator: Draft202012Validator) -> tuple[int, int, int]:
    failures = 0
    counts = {"valid": 0, "invalid": 0}
    for group, should_validate in (("valid", True), ("invalid", False)):
        paths = sorted((PROFILE_ROOT / "fixtures" / group).glob("*.json"))
        if not paths:
            print(f"profiles/cpp/0.1/fixtures/{group}: no fixtures", file=sys.stderr)
            failures += 1
        counts[group] = len(paths)
        for path in paths:
            payload = load(path)
            errors = list(validator.iter_errors(payload))
            if should_validate != (not errors):
                failures += 1
                error = best_match(errors)
                detail = error.message if error else "unexpectedly validated"
                print(f"{path.relative_to(ROOT)}: {detail}", file=sys.stderr)
            elif should_validate and payload.get("kind") == "special-member":
                issues = signature_issues(payload.get("operation"), payload.get("signature"))
                expected = disambiguator(payload.get("signature"))
                if payload.get("memberDisambiguator") != expected:
                    issues.append("member disambiguator does not hash the canonical signature")
                for issue in issues:
                    failures += 1
                    print(f"{path.relative_to(ROOT)}: {issue}", file=sys.stderr)
    alias = load(PROFILE_ROOT / "fixtures" / "valid" / "std-string-alias.json")
    for issue in std_string_alias_issues(alias):
        failures += 1
        print(f"std-string-alias.json: {issue}", file=sys.stderr)
    return failures, counts["valid"], counts["invalid"]


def validate_signature_inputs(validator: Draft202012Validator) -> tuple[int, int]:
    failures = 0
    records = load(SIGNATURE_INPUTS).get("records", [])
    signature_validator = validator.evolve(schema=validator.schema["$defs"]["callableSignature"])
    by_case: dict[str, dict[str, object]] = {}
    for record in records:
        case = record.get("case", "<missing>")
        signature = record.get("canonicalInput")
        errors = list(signature_validator.iter_errors(signature))
        issues = signature_issues(case, signature)
        expected = disambiguator(signature)
        if errors or issues or record.get("expectedDisambiguator") != expected:
            failures += 1
            detail = errors[0].message if errors else issues[0] if issues else "digest mismatch"
            print(f"{SIGNATURE_INPUTS.relative_to(ROOT)}:{case}: {detail}", file=sys.stderr)
        by_case[case] = record
    if set(by_case) != {"copy-constructor", "copy-assignment", "move-constructor"}:
        failures += 1
        print("C++ signature inputs must contain exactly the three proven operations", file=sys.stderr)
    fixture = load(COPY_FIXTURE)
    constructor = by_case.get("copy-constructor", {})
    if (
        fixture.get("signature") != constructor.get("canonicalInput")
        or fixture.get("memberDisambiguator") != constructor.get("expectedDisambiguator")
    ):
        failures += 1
        print("copy-constructor fixture and canonical input disagree", file=sys.stderr)

    # Assert the semantic checks actually reject the native near-miss shapes.
    if by_case:
        exact = next(iter(by_case.values()))["canonicalInput"]
        wrong_hash = disambiguator({**exact, "callableKind": "method"})
        if wrong_hash == next(iter(by_case.values()))["expectedDisambiguator"]:
            failures += 1
            print("canonical digest does not distinguish callable kind", file=sys.stderr)
    return failures, len(records)


def validate_resolution_input() -> int:
    """Recompute the compiler-argument and full resolution-context digests."""
    failures = 0
    manifest = load(RESOLUTION_INPUT)
    context = load(RESOLUTION_FIXTURE)
    arguments_digest = hashlib.sha256(
        canonical_bytes(manifest.get("orderedCompilerArguments"))
    ).hexdigest()
    if (
        manifest.get("expectedCompileArgumentsDigest") != arguments_digest
        or context.get("compileArgumentsDigest") != arguments_digest
    ):
        failures += 1
        print("C/C++ compiler-argument digest does not match its canonical input", file=sys.stderr)
    context_digest = hashlib.sha256(canonical_bytes(context)).hexdigest()
    for path in (
        COPY_FIXTURE,
        PROFILE_ROOT / "fixtures" / "valid" / "std-string-alias.json",
    ):
        if load(path).get("resolutionContext", {}).get("contextDigest") != context_digest:
            failures += 1
            print(f"{path.relative_to(ROOT)}: resolution context digest mismatch", file=sys.stderr)
    expected_path = ROOT / str(manifest.get("resolutionContextFixture", ""))
    if expected_path != RESOLUTION_FIXTURE:
        failures += 1
        print("C/C++ resolution input names the wrong fixture", file=sys.stderr)
    return failures


def validate_contract_rejections(validator: Draft202012Validator) -> int:
    """Exercise fail-closed rules that prose or JSON shape alone cannot prove."""
    failures = 0
    constructor = load(COPY_FIXTURE)

    incomplete = deepcopy(constructor)
    incomplete["resolutionContext"]["headerClosure"] = "partial"
    if not list(validator.iter_errors(incomplete)):
        failures += 1
        print("contract check accepted a special member under partial header closure", file=sys.stderr)

    c_application = deepcopy(constructor)
    c_application["language"] = "c"
    c_application["resolutionContext"]["language"] = "c"
    if not list(validator.iter_errors(c_application)):
        failures += 1
        print("contract check accepted a C++ special member for C", file=sys.stderr)

    custom_owner = deepcopy(constructor["signature"])
    custom_owner["owner"]["descriptors"][0]["name"] = "custom"
    parameter_owner = custom_owner["parameters"][0]["referent"]["type"]["symbol"]
    parameter_owner["descriptors"][0]["name"] = "custom"
    if not signature_issues("copy-constructor", custom_owner):
        failures += 1
        print("contract check accepted a same-named custom owner", file=sys.stderr)

    wrong_signature = deepcopy(constructor["signature"])
    wrong_signature["parameters"][0]["referenceKind"] = "rvalue"
    if not signature_issues("copy-constructor", wrong_signature):
        failures += 1
        print("contract check accepted an rvalue copy-constructor parameter", file=sys.stderr)

    name_only = deepcopy(constructor["signature"])
    name_only["owner"] = {"name": "std.basic_string"}
    if not signature_issues("copy-constructor", name_only):
        failures += 1
        print("contract check accepted name-only owner identity", file=sys.stderr)
    return failures


def validate_value_transfer_integration(validator: Draft202012Validator) -> int:
    """Bind the portable transfer fixture to exact C++ applicability and identity."""
    failures = 0
    document = load(VALUE_TRANSFER_FIXTURE)
    model = document["semanticModels"][0]
    uses = {
        (use.get("identifier"), use.get("version")): use
        for use in model.get("vocabularyUses", [])
    }
    for identifier in ("csmi.c-cpp-resolution", "csmi.cpp"):
        use = uses.get((identifier, "0.1.0"), {})
        if (
            use.get("schema") != "https://csmi.brokk.ai/schema/profiles/cpp/0.1/schema.json"
            or use.get("requirement") != "required"
        ):
            failures += 1
            print(
                f"{VALUE_TRANSFER_FIXTURE.relative_to(ROOT)}: missing exact required {identifier} use",
                file=sys.stderr,
            )

    contexts = [
        constraint.get("value")
        for constraint in model.get("compatibilityConstraints", [])
        if (constraint.get("vocabulary"), constraint.get("version"))
        == ("csmi.c-cpp-resolution", "0.1.0")
    ]
    if (
        len(contexts) != 1
        or list(validator.iter_errors(contexts[0]))
        or contexts[0] != load(RESOLUTION_FIXTURE)
    ):
        failures += 1
        print(
            f"{VALUE_TRANSFER_FIXTURE.relative_to(ROOT)}: invalid exact C/C++ resolution context",
            file=sys.stderr,
        )

    selectors = model.get("artifactSelectors", [])
    symbols = {symbol.get("id"): symbol for symbol in model.get("symbols", [])}
    for symbol_id in ("basicString", "copyConstructor"):
        symbol = symbols.get(symbol_id, {})
        inherited_key = {
            "artifactSelectors": selectors,
            "scheme": symbol.get("scheme"),
            "schemeVersion": symbol.get("schemeVersion"),
            "stability": symbol.get("stability"),
            "descriptors": symbol.get("descriptors"),
        }
        for issue in symbol_key_issues(inherited_key):
            failures += 1
            print(f"{VALUE_TRANSFER_FIXTURE.relative_to(ROOT)}:{symbol_id}: {issue}", file=sys.stderr)
    primary = symbols.get("basicString", {})
    if not exact_std_template(primary, "basic_string", 3):
        failures += 1
        print(
            f"{VALUE_TRANSFER_FIXTURE.relative_to(ROOT)}: transfer owner is not exact std::basic_string",
            file=sys.stderr,
        )
    constructor_descriptors = symbols.get("copyConstructor", {}).get("descriptors", [])
    expected = load(SIGNATURE_INPUTS)["records"][0]["expectedDisambiguator"]
    if not constructor_descriptors or constructor_descriptors[-1].get("disambiguator") != expected:
        failures += 1
        print(
            f"{VALUE_TRANSFER_FIXTURE.relative_to(ROOT)}: transfer operation lacks canonical copy identity",
            file=sys.stderr,
        )
    return failures


def main() -> int:
    schema = load(SCHEMA_PATH)
    try:
        Draft202012Validator.check_schema(schema)
    except SchemaError as error:
        print(f"{SCHEMA_PATH.relative_to(ROOT)}: invalid schema: {error.message}", file=sys.stderr)
        return 1
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    fixture_failures, valid_count, invalid_count = validate_profile_fixtures(validator)
    signature_failures, signature_count = validate_signature_inputs(validator)
    resolution_failures = validate_resolution_input()
    contract_failures = validate_contract_rejections(validator)
    integration_failures = validate_value_transfer_integration(validator)
    failures = (
        fixture_failures
        + signature_failures
        + resolution_failures
        + contract_failures
        + integration_failures
    )
    if failures:
        print(f"C++ profile validation failed for {failures} expectation(s)", file=sys.stderr)
        return 1
    print(
        "C++ profile validation passed: "
        f"{valid_count} valid, {invalid_count} structurally rejected, "
        f"{signature_count} canonical signatures"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
