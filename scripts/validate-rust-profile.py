#!/usr/bin/env python3
"""Check Rust-profile semantics that JSON Schema cannot express."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import unicodedata
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker


ROOT = Path(__file__).resolve().parents[1]
PROFILE_SCHEMA = ROOT / "profiles" / "rust" / "0.1" / "schema.json"
PROFILE_SCHEMA_ID = "https://csmi.brokk.ai/schema/profiles/rust/0.1/schema.json"
TARGET_KINDS = {"lib", "bin", "example", "test", "bench", "proc-macro", "build-script"}
DESCRIPTOR_KINDS = {
    "module", "struct", "enum", "union", "trait", "type-alias", "function",
    "method", "associated-function", "const", "static", "variant",
    "macro-rules", "macro", "proc-macro-function", "proc-macro-derive",
    "proc-macro-attribute", "type-parameter", "const-parameter",
    "lifetime-parameter",
}


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_sha256(value: object) -> str:
    # The implementation-key vocabulary contains only integers, strings,
    # arrays, and objects, so this is the RFC 8785 serialization for fixtures.
    encoded = json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def is_crate_root_disambiguator(value: str) -> bool:
    target_kind, separator, crate_name = value.partition(":")
    if separator != ":" or target_kind not in TARGET_KINDS or not crate_name:
        return False
    unescaped = re.sub(r"%[0-9A-F]{2}", "", crate_name)
    return ":" not in unescaped and "%" not in unescaped


def full_key(model: dict[str, object], symbol: dict[str, object]) -> dict[str, object]:
    return {
        "artifactSelectors": model["artifactSelectors"],
        "scheme": symbol["scheme"],
        "schemeVersion": symbol["schemeVersion"],
        "stability": symbol["stability"],
        "descriptors": symbol["descriptors"],
    }


def rust_semantic_issues(
    document: dict[str, object], validator: Draft202012Validator
) -> list[str]:
    issues: list[str] = []
    for model_index, model_value in enumerate(document.get("semanticModels", [])):
        model = model_value
        symbols = {symbol["id"]: symbol for symbol in model.get("symbols", [])}
        declarations = {
            declaration["symbol"]: declaration
            for declaration in model.get("declarations", [])
        }
        rust_symbols = [
            symbol
            for symbol in symbols.values()
            if symbol.get("scheme") == "csmi.rust.source-item"
        ]
        rust_facts = [
            fact
            for fact in model.get("extensionFacts", [])
            if fact.get("vocabulary") == "csmi.rust"
        ]
        rust_constraints = [
            constraint
            for constraint in model.get("compatibilityConstraints", [])
            if constraint.get("vocabulary") == "csmi.rust"
        ]
        if not (rust_symbols or rust_facts or rust_constraints):
            continue

        prefix = f"semanticModels[{model_index}]"
        uses = [
            use
            for use in model.get("vocabularyUses", [])
            if use.get("identifier") == "csmi.rust" and use.get("version") == "0.1.0"
        ]
        if len(uses) != 1 or uses[0].get("schema") != PROFILE_SCHEMA_ID:
            issues.append(f"{prefix}: requires exactly one csmi.rust 0.1.0 profile use")
        elif rust_symbols and uses[0].get("requirement") != "required":
            issues.append(f"{prefix}: Rust identity semantics require the profile use")

        for constraint in rust_constraints:
            errors = list(validator.iter_errors(constraint.get("value")))
            if errors:
                issues.append(f"{prefix}: Rust compatibility payload fails its profile schema")
            else:
                value = constraint["value"]
                if value["enabledFeatures"] != sorted(value["enabledFeatures"]):
                    issues.append(f"{prefix}: enabled feature set is not canonically ordered")
                cfg_sort_key = lambda atom: (atom["key"], atom.get("value", ""))
                if value["cfgAtoms"] != sorted(value["cfgAtoms"], key=cfg_sort_key):
                    issues.append(f"{prefix}: cfg atom set is not canonically ordered")

        for symbol in rust_symbols:
            descriptors = symbol.get("descriptors", [])
            crate_roots = [
                descriptor
                for descriptor in descriptors
                if is_crate_root_disambiguator(descriptor.get("disambiguator", ""))
            ]
            if not descriptors or len(crate_roots) != 1 or crate_roots[0] is not descriptors[0] or descriptors[0].get("role") != "namespace" or descriptors[0].get("name") != "crate":
                issues.append(f"{prefix}.{symbol['id']}: invalid crate-root descriptor")
            for descriptor in descriptors:
                name = descriptor.get("name", "")
                if name.startswith("r#") or name != unicodedata.normalize("NFC", name):
                    issues.append(f"{prefix}.{symbol['id']}: descriptor name is not normalized")
            for descriptor in descriptors[1:]:
                role = descriptor.get("role")
                kind = descriptor.get("disambiguator")
                if role in {"type-parameter", "value-parameter"}:
                    allowed = {
                        "type-parameter": {"type-parameter", "lifetime-parameter"},
                        "value-parameter": {"const-parameter"},
                    }[role]
                    if not descriptor.get("name", "").isdigit() or kind not in allowed:
                        issues.append(f"{prefix}.{symbol['id']}: invalid generic-parameter descriptor")
                elif kind not in DESCRIPTOR_KINDS and not (
                    role == "meta" and descriptor.get("name") == "impl" and re.fullmatch(r"jcs-sha256:[0-9a-f]{64}", kind or "")
                ):
                    issues.append(f"{prefix}.{symbol['id']}: invalid descriptor kind")
            declaration = declarations.get(symbol["id"])
            category = (declaration or {}).get("category")
            expected_role = {"type-alias": "type", "value": "term"}.get(category, category)
            if declaration and descriptors and descriptors[-1].get("role") != expected_role:
                issues.append(f"{prefix}.{symbol['id']}: terminal descriptor role disagrees with declaration category")
            if descriptors and descriptors[-1].get("disambiguator") == "associated-function":
                callable_shape = (declaration or {}).get("callable", {})
                if callable_shape.get("kind") != "function" or "receiver" in callable_shape:
                    issues.append(f"{prefix}.{symbol['id']}: associated function has a receiver")
            if symbol.get("stability") == "artifact-local" and any(
                not selector.get("digests") for selector in model["artifactSelectors"]
            ):
                issues.append(f"{prefix}.{symbol['id']}: artifact-local identity lacks exact selector digests")

        selector_purls = {selector["purl"] for selector in model["artifactSelectors"]}
        unavailable_generation_scopes: list[dict[str, object]] = []
        for fact in rust_facts:
            payload = fact.get("payload")
            if list(validator.iter_errors(payload)):
                issues.append(f"{prefix}: {fact.get('family')} payload fails its profile schema")
                continue
            kind = payload["kind"]
            if kind == "reexport":
                for field in ("exportingModule", "target"):
                    if payload[field] not in symbols:
                        issues.append(f"{prefix}: reexport {field} does not name a local symbol")
            elif kind == "crate-target" and payload["packagePurl"] not in selector_purls:
                issues.append(f"{prefix}: crate target is not linked to an enclosing package selector")
            elif kind == "implementation":
                for field in ("implementation", "implementingType", "trait"):
                    if payload.get(field) not in symbols:
                        issues.append(f"{prefix}: implementation {field} does not name a local symbol")
                if payload.get("trait") in symbols:
                    expected = full_key(model, symbols[payload["trait"]])
                    if payload["identityKey"]["trait"] != expected:
                        issues.append(f"{prefix}: implementation trait key is not the referenced local symbol")
                type_id = payload.get("implementingType")
                pattern = payload["identityKey"]["implementingType"]
                if type_id in symbols and pattern.get("kind") == "declared":
                    if pattern.get("symbol") != full_key(model, symbols[type_id]):
                        issues.append(f"{prefix}: implementation self-type key is not the referenced local symbol")
                impl_id = payload.get("implementation")
                if impl_id in symbols:
                    descriptor = symbols[impl_id]["descriptors"][-1]
                    expected_digest = f"jcs-sha256:{canonical_sha256(payload['identityKey'])}"
                    if descriptor.get("disambiguator") != expected_digest:
                        issues.append(f"{prefix}: implementation descriptor digest is inconsistent")
                for mapping in payload.get("associatedItems", []):
                    if mapping["providedItem"] not in symbols or mapping["traitItem"] not in symbols:
                        issues.append(f"{prefix}: associated-item mapping does not use local symbols")
            elif kind == "generation":
                if payload["item"] not in symbols:
                    issues.append(f"{prefix}: generated item does not name a local symbol")
                if "generator" in payload and payload["generator"] not in symbols:
                    issues.append(f"{prefix}: generator does not name a local symbol")
                if payload["portability"] == "unavailable":
                    unavailable_generation_scopes.append(fact.get("scope", {}))
                elif len(rust_constraints) != 1:
                    issues.append(f"{prefix}: portable generation requires one Rust configuration")
            elif kind == "native-mapping":
                if payload["source"] not in symbols:
                    issues.append(f"{prefix}: native mapping does not name a local symbol")
                if payload["status"] == "conditional" and len(rust_constraints) != 1:
                    issues.append(f"{prefix}: conditional native mapping requires one Rust configuration")
            elif kind == "sysroot-crate" and payload["artifactPurl"] not in selector_purls:
                issues.append(f"{prefix}: sysroot payload is not linked to an enclosing selector")

        for statement in model.get("completenessStatements", []):
            if (
                statement.get("vocabulary") == "csmi.rust"
                and statement.get("family") == "generation"
                and statement.get("status") == "complete"
                and statement.get("scope") in unavailable_generation_scopes
            ):
                issues.append(f"{prefix}: unavailable generation cannot have complete coverage")
    return issues


def main() -> int:
    validator = Draft202012Validator(load(PROFILE_SCHEMA), format_checker=FormatChecker())
    expectations = {
        "valid": False,
        "semantic-invalid": True,
    }
    failures = 0
    counts: dict[str, int] = {}
    for group, should_have_issues in expectations.items():
        paths = sorted((ROOT / "fixtures" / group).glob("rust-*.json"))
        counts[group] = len(paths)
        if not paths:
            print(f"fixtures/{group}: no Rust fixtures found", file=sys.stderr)
            failures += 1
            continue
        for path in paths:
            issues = rust_semantic_issues(load(path), validator)
            if bool(issues) != should_have_issues:
                failures += 1
                detail = "; ".join(issues) if issues else "no semantic issue detected"
                print(f"{path.relative_to(ROOT)}: {detail}", file=sys.stderr)
    if failures:
        print(f"Rust semantic validation failed for {failures} fixture(s)", file=sys.stderr)
        return 1
    print(
        "Rust semantic validation passed: "
        f"{counts['valid']} valid, {counts['semantic-invalid']} rejected"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
