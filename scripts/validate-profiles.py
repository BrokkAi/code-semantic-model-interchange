#!/usr/bin/env python3
"""Validate every profile schema plus structural and executable semantic cases."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import urlparse

from jsonschema import Draft202012Validator, FormatChecker
from jsonschema.exceptions import SchemaError, best_match


ROOT = Path(__file__).resolve().parents[1]
JAVA_PROFILE_ROOT = ROOT / "profiles" / "java-jvm" / "0.1"
JAVA_FIXTURE_ROOT = ROOT / "fixtures" / "profiles" / "java-jvm"
JAVA_CORE_FIXTURE = ROOT / "fixtures" / "valid" / "java-jvm-mapping.json"


def load_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def absolute_uri(value: object) -> bool:
    return isinstance(value, str) and bool(urlparse(value).scheme)


def java_semantic_errors(schema_name: str, instance: object) -> list[str]:
    if not isinstance(instance, dict):
        return ["payload is not an object"]
    errors: list[str] = []
    if schema_name == "jvm-compatibility":
        constraints = instance.get("constraints", {})
        for name in ("javaRelease", "classFileMajor"):
            bounds = constraints.get(name, {})
            if "minimum" in bounds and "maximum" in bounds:
                if bounds["minimum"] > bounds["maximum"]:
                    errors.append(f"{name} minimum exceeds maximum")
        vendor = constraints.get("jvmVendor")
        if vendor is not None and not absolute_uri(vendor):
            errors.append("jvmVendor is not an absolute URI")
    elif schema_name == "java-jvm-mapping":
        for evidence in instance.get("evidence", []):
            if not absolute_uri(evidence.get("producer")):
                errors.append("mapping evidence producer is not an absolute URI")
    elif schema_name == "java-source-identity":
        signature = instance.get("declaration", {}).get("signature", {})
        source_types = list(signature.get("parameterTypes", []))
        receiver = signature.get("receiverType")
        if receiver is not None:
            source_types.append(receiver)
        for source_type in source_types:
            canonical_name = source_type.get("canonicalName", "")
            if re.search(r"\s|[/;\[<>]", canonical_name.replace("[]", "")):
                errors.append("canonicalName is not a canonical source type identity")
            if instance.get("language") == "java" and source_type.get("parameterMode") == "vararg":
                errors.append("Java varargs must be normalized to array value parameters")
    elif schema_name == "jvm-binary-identity":
        entity = instance.get("binaryEntity", {})
        name = entity.get("name")
        descriptor = entity.get("descriptor", "")
        if name == "<init>" and not descriptor.endswith("V"):
            errors.append("<init> descriptor must return void")
        if name == "<clinit>" and descriptor != "()V":
            errors.append("<clinit> descriptor must be ()V")
        variant = instance.get("variant", {})
        path = variant.get("entryPath", "")
        release = variant.get("release")
        match = re.match(r"^META-INF/versions/([1-9][0-9]*)/", path)
        if match and release != int(match.group(1)):
            errors.append("multi-release path version differs from selected release")
        if match and release < 9:
            errors.append("multi-release entry version must be at least 9")
    return errors


def validate_python_profiles() -> tuple[int, dict[str, int]]:
    failures = 0
    counts = {"schemas": 0, "valid": 0, "invalid": 0}
    for schema_path in sorted(ROOT.glob("profiles/*/*/schema.json")):
        schema = load_json(schema_path)
        counts["schemas"] += 1
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
                # Some profiles carry a complete semantic document to exercise
                # attachment and cross-record rules. Their dedicated validator
                # owns core-plus-profile validation; this generic pass validates
                # the raw payload fixtures beside each schema.
                if (
                    group == "valid"
                    and isinstance(instance, dict)
                    and instance.get("documentType") == "semantic-document"
                ):
                    continue
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
            failures += validate_python_documents(validator)
    return failures, counts


def validate_python_documents(validator: Draft202012Validator) -> int:
    failures = 0
    for document_path in sorted((ROOT / "fixtures" / "valid").glob("*.json")):
        document = load_json(document_path)
        if not isinstance(document, dict) or document.get("documentType") != "semantic-document":
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
    return failures


def validate_java_profiles() -> tuple[int, dict[str, int]]:
    failures = 0
    counts = {"schemas": 0, "valid": 0, "invalid": 0, "semantic-invalid": 0}
    validators: dict[str, Draft202012Validator] = {}
    for schema_path in sorted(JAVA_PROFILE_ROOT.glob("*.schema.json")):
        schema = load_json(schema_path)
        counts["schemas"] += 1
        try:
            Draft202012Validator.check_schema(schema)
        except SchemaError as error:
            failures += 1
            print(f"{schema_path.relative_to(ROOT)}: invalid schema: {error.message}", file=sys.stderr)
            continue
        validators[schema_path.name.removesuffix(".schema.json")] = Draft202012Validator(
            schema, format_checker=FormatChecker()
        )
    for group, should_validate, should_be_semantically_valid in (
        ("valid", True, True),
        ("invalid", False, False),
        ("semantic-invalid", True, False),
    ):
        fixtures = sorted((JAVA_FIXTURE_ROOT / group).glob("*.json"))
        if not fixtures:
            failures += 1
            print(f"{(JAVA_FIXTURE_ROOT / group).relative_to(ROOT)}: no fixtures", file=sys.stderr)
        counts[group] += len(fixtures)
        for fixture_path in fixtures:
            wrapper = load_json(fixture_path)
            if not isinstance(wrapper, dict) or "$profileSchema" not in wrapper:
                failures += 1
                print(f"{fixture_path.relative_to(ROOT)}: missing $profileSchema", file=sys.stderr)
                continue
            instance = dict(wrapper)
            schema_name = instance.pop("$profileSchema")
            validator = validators.get(schema_name)
            if validator is None:
                failures += 1
                print(f"{fixture_path.relative_to(ROOT)}: unknown schema {schema_name!r}", file=sys.stderr)
                continue
            structural_errors = list(validator.iter_errors(instance))
            if should_validate != (not structural_errors):
                failures += 1
                detail = structural_errors[0].message if structural_errors else "unexpectedly validated"
                print(f"{fixture_path.relative_to(ROOT)}: {detail}", file=sys.stderr)
                continue
            if should_validate:
                semantic_errors = java_semantic_errors(schema_name, instance)
                if should_be_semantically_valid != (not semantic_errors):
                    failures += 1
                    detail = semantic_errors[0] if semantic_errors else "unexpected semantic validity"
                    print(f"{fixture_path.relative_to(ROOT)}: {detail}", file=sys.stderr)
    failures += validate_java_document(validators)
    return failures, counts


def validate_java_document(validators: dict[str, Draft202012Validator]) -> int:
    failures = 0
    document = load_json(JAVA_CORE_FIXTURE)
    expected = {
        "csmi.java-source-identity": "java-source-identity",
        "csmi.jvm-binary-identity": "jvm-binary-identity",
        "csmi.java-jvm-mapping": "java-jvm-mapping",
        "csmi.jvm-compatibility": "jvm-compatibility",
    }
    for model in document.get("semanticModels", []):
        uses = {use.get("identifier"): use for use in model.get("vocabularyUses", [])}
        for identifier, schema_name in expected.items():
            expected_uri = (
                "https://csmi.brokk.ai/schema/profiles/java-jvm/0.1/"
                f"{schema_name}.schema.json"
            )
            use = uses.get(identifier)
            if not use or use.get("version") != "0.1" or use.get("schema") != expected_uri:
                failures += 1
                print(f"{JAVA_CORE_FIXTURE.relative_to(ROOT)}: missing exact use {identifier}", file=sys.stderr)
        for constraint in model.get("compatibilityConstraints", []):
            if constraint.get("vocabulary") == "csmi.jvm-compatibility":
                value = constraint.get("value")
                errors = list(validators["jvm-compatibility"].iter_errors(value))
                semantic_errors = java_semantic_errors("jvm-compatibility", value)
                if errors or semantic_errors:
                    failures += 1
                    print(f"{JAVA_CORE_FIXTURE.relative_to(ROOT)}: invalid compatibility payload", file=sys.stderr)
        for fact in model.get("extensionFacts", []):
            if fact.get("vocabulary") == "csmi.java-jvm-mapping":
                payload = fact.get("payload")
                errors = list(validators["java-jvm-mapping"].iter_errors(payload))
                semantic_errors = java_semantic_errors("java-jvm-mapping", payload)
                if errors or semantic_errors:
                    failures += 1
                    print(f"{JAVA_CORE_FIXTURE.relative_to(ROOT)}: invalid mapping payload", file=sys.stderr)
    return failures


def main() -> int:
    python_failures, python_counts = validate_python_profiles()
    java_failures, java_counts = validate_java_profiles()
    failures = python_failures + java_failures
    if failures:
        print(f"Profile validation failed for {failures} expectation(s)", file=sys.stderr)
        return 1
    print(
        "Profile validation passed: "
        f"{python_counts['schemas'] + java_counts['schemas']} schemas, "
        f"{python_counts['valid'] + java_counts['valid']} valid, "
        f"{python_counts['invalid'] + java_counts['invalid']} structurally rejected, "
        f"{java_counts['semantic-invalid']} semantic-invalid rejected by profile semantics"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
