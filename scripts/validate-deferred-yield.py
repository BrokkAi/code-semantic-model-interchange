#!/usr/bin/env python3
"""Validate the deferred-yield profile and exercise an independent consumer."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "deferred-yield" / "0.1"
SCHEMA_ID = "https://csmi.brokk.ai/schema/profiles/deferred-yield/0.1/schema.json"
VOCABULARY = "csmi.deferred-yield"
VERSION = "0.1.0"


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def uncertain(value):
    if isinstance(value, dict):
        return value.get("kind") in {"unknown", "unsupported"} or any(uncertain(v) for v in value.values())
    return isinstance(value, list) and any(uncertain(v) for v in value)


def shape_at(location, roots):
    shape = roots.get((location["callable"], canonical(location["root"])))
    if shape is None:
        raise ValueError("location lacks root-shape evidence")
    for step in location.get("projection", {}).get("steps", []):
        if step["kind"] == "entry":
            if shape["kind"] != "keyed":
                raise ValueError("entry requires keyed source")
            shape = {"kind": "entry", "key": shape["key"], "value": shape["value"]}
        elif step["kind"] in {"entry-key", "entry-value"}:
            if shape["kind"] != "entry":
                raise ValueError("entry member requires entry")
            shape = shape["key" if step["kind"] == "entry-key" else "value"]
    return shape


def payload_issues(payload, declarations=None):
    issues = []
    roots = {}
    for item in payload.get("roots", []):
        key = (item["callable"], canonical(item["root"]))
        if key in roots:
            issues.append("duplicate root shape")
        roots[key] = item["shape"]
    factory, resume, handle_type = (payload.get(k) for k in ("factory", "resume", "handleType"))
    if factory == resume:
        issues.append("factory and resume must be distinct")
    if declarations is not None:
        if declarations.get(factory, {}).get("category") != "callable" or declarations.get(resume, {}).get("category") != "callable":
            issues.append("factory and resume must resolve to callables")
        if declarations.get(handle_type, {}).get("category") != "type":
            issues.append("handleType must resolve to a type")
    construction = payload.get("construction", {})
    resume_contract = payload.get("resumeContract", {})
    if construction.get("source", {}).get("callable") != factory or construction.get("source", {}).get("root", {}).get("phase") != "input":
        issues.append("construction source must be a factory input")
    handle = construction.get("handle", {})
    if handle.get("callable") != factory or handle.get("root", {}).get("phase") != "output" or handle.get("root", {}).get("role") != "result":
        issues.append("construction handle must be a factory result")
    handle_input = resume_contract.get("handleInput", {})
    item = resume_contract.get("yieldedResult", {})
    if handle_input.get("callable") != resume or handle_input.get("root", {}).get("phase") != "input":
        issues.append("resume handle must be a resume input")
    if item.get("callable") != resume or item.get("root", {}).get("phase") != "output" or item.get("root", {}).get("role") != "result":
        issues.append("yielded item must be a resume result")
    flow = resume_contract.get("factoryResultFlow", {})
    if flow.get("factoryResult") != handle or flow.get("resumeInput") != handle_input:
        issues.append("factory-result flow endpoints must match handle endpoints")
    try:
        handle_shape = shape_at(handle, roots)
        resume_shape = shape_at(handle_input, roots)
        if handle_shape != resume_shape or handle_shape.get("type", {}).get("symbol") != handle_type:
            issues.append("handle endpoint shapes must share exact handleType")
        item_shape = shape_at(item, roots)
    except (KeyError, ValueError) as error:
        issues.append(str(error))
        item_shape = None
    retention = construction.get("retention")
    positions, roles = [], []
    for member in payload.get("yield", {}).get("members", []):
        positions.append(member["position"])
        roles.append(member["role"])
        try:
            source_shape = shape_at(member["source"], roots)
        except ValueError as error:
            issues.append(str(error))
            source_shape = None
        if member["source"].get("callable") != factory:
            issues.append("yield member source must belong to factory source")
        steps = member["source"].get("projection", {}).get("steps", [])
        expected_step = {"key": "entry-key", "value": "entry-value"}.get(member["role"])
        if expected_step and (not steps or steps[-1].get("kind") != expected_step):
            issues.append("entry member role must match its exact source projection")
        delivery = member["delivery"]
        if retention == "borrowed-shared" and delivery in {"exclusive-borrow", "move"}:
            issues.append("shared retention cannot justify exclusive or move delivery")
        if retention == "borrowed-exclusive" and delivery == "move":
            issues.append("borrowed retention cannot justify move delivery")
        if item_shape and item_shape.get("kind") == "product" and member["position"] < len(item_shape["components"]):
            destination_shape = item_shape["components"][member["position"]]
            if delivery != "derived" and source_shape is not None and not uncertain(source_shape) and not uncertain(destination_shape) and source_shape != destination_shape:
                issues.append("non-derived member source and item shapes must agree")
    if len(positions) != len(set(positions)) or positions != list(range(len(positions))):
        issues.append("yield member positions must be unique contiguous order")
    if len(roles) != len(set(roles)) and "item" not in roles:
        issues.append("entry roles must be unique")
    if item_shape and item_shape.get("kind") == "product" and len(positions) > len(item_shape["components"]):
        issues.append("yield member position exceeds item shape")
    return issues


def document_issues(document):
    issues = []
    for model in document.get("semanticModels", []):
        declarations = {item["symbol"]: item for item in model.get("declarations", [])}
        use = next((item for item in model.get("vocabularyUses", []) if item.get("identifier") == VOCABULARY), None)
        facts = [item for item in model.get("extensionFacts", []) if item.get("vocabulary") == VOCABULARY]
        if not use or use.get("version") != VERSION or use.get("schema") != SCHEMA_ID or use.get("requirement") != "required":
            issues.append("exact required vocabulary use missing")
            affected = set()
        else:
            affected = {(item.get("family"), canonical(item.get("scope"))) for item in use.get("affects", []) if item.get("kind") == "fact-family"}
        fact_scopes = {}
        for fact in facts:
            payload = fact.get("payload", {})
            scope = {"factory": payload.get("factory"), "resume": payload.get("resume"), "handleType": payload.get("handleType")}
            key = ("deferred-yields", canonical(scope))
            if fact.get("version") != VERSION or fact.get("family") != key[0] or fact.get("scope") != scope:
                issues.append("fact version family or scope mismatch")
            if key not in affected:
                issues.append("fact absent from exact affects")
            issues.extend(payload_issues(payload, declarations))
            fact_scopes.setdefault(key, []).append(payload)
        seen = set()
        for statement in model.get("completenessStatements", []):
            if statement.get("vocabulary") != VOCABULARY:
                continue
            key = (statement.get("family"), canonical(statement.get("scope")))
            if statement.get("version") != VERSION or key not in affected or key[0] != "deferred-yields" or set(statement.get("scope", {})) != {"factory", "resume", "handleType"}:
                issues.append("invalid completeness scope or version")
            if key in seen:
                issues.append("duplicate completeness scope")
            seen.add(key)
            facts_here = fact_scopes.get(key, [])
            if statement.get("status") == "complete" and (any(uncertain(item) for item in facts_here) or len({canonical(item) for item in facts_here}) > 1):
                issues.append("complete scope contains uncertainty or conflict")
    return issues


def make_document(payload, status="complete"):
    symbols = []
    for identifier, role in [("Map", "type"), ("Iter", "type"), ("Key", "type"), ("Value", "type"), ("iter", "term"), ("next", "term")]:
        symbols.append({"id": identifier, "scheme": "example.deferred-yield", "schemeVersion": "0.1.0", "descriptors": [{"name": identifier, "role": role}], "stability": "portable"})
    declarations = [
        {"symbol": "Map", "category": "type"}, {"symbol": "Iter", "category": "type"},
        {"symbol": "Key", "category": "type"}, {"symbol": "Value", "category": "type"},
        {"symbol": "iter", "category": "callable", "callable": {"kind": "method", "parameters": [], "results": [{"position": 0}], "receiver": {"kind": "instance", "type": {"kind": "reference", "symbol": "Map"}}}},
        {"symbol": "next", "category": "callable", "callable": {"kind": "method", "parameters": [], "results": [{"position": 0}], "receiver": {"kind": "instance", "type": {"kind": "reference", "symbol": "Iter"}}}},
    ]
    scope = {"factory": payload["factory"], "resume": payload["resume"], "handleType": payload["handleType"]}
    completeness = {"vocabulary": VOCABULARY, "version": VERSION, "family": "deferred-yields", "scope": scope, "status": status}
    if status == "partial":
        completeness["limitations"] = [{"kind": "unsupported-semantics"}]
    return {
        "documentType": "semantic-document", "schema": "https://csmi.brokk.ai/schema/0.1/schema.json",
        "semanticModelVersion": "0.1", "serializationVersion": "0.1-json",
        "provenanceRecords": [{"id": "fixture", "producer": {"identifier": "https://csmi.brokk.ai/conformance/deferred-yield", "version": VERSION}, "generationMethod": "manual-authoring"}],
        "defaultProvenance": "fixture",
        "semanticModels": [{"artifactSelectors": [{"purl": "pkg:generic/deferred-yield-fixture@1.0.0"}], "symbols": symbols, "declarations": declarations,
            "vocabularyUses": [{"identifier": VOCABULARY, "version": VERSION, "schema": SCHEMA_ID, "requirement": "required", "affects": [{"kind": "fact-family", "family": "deferred-yields", "scope": scope}]}],
            "extensionFacts": [{"vocabulary": VOCABULARY, "version": VERSION, "family": "deferred-yields", "scope": scope, "payload": payload}],
            "completenessStatements": [completeness,
                {"family": "declaration-aspects", "scope": {"symbol": "iter", "aspect": "callable-shape"}, "status": "complete"},
                {"family": "declaration-aspects", "scope": {"symbol": "next", "aspect": "callable-shape"}, "status": "complete"}]}]
    }


def independent_yields(payload, source):
    assert payload["yield"]["timing"] == "after-construction"
    values = []
    for key, value in source.items():
        projected = {"key": key, "value": value}
        values.append(tuple(projected[m["role"]] for m in payload["yield"]["members"]))
    return values


def main():
    schema = load(PROFILE / "schema.json")
    core_schema = load(ROOT / "spec" / "0.1" / "schema.json")
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    core = Draft202012Validator(core_schema, format_checker=FormatChecker())
    counts = {}
    for group, structural, semantic in (("valid", True, True), ("invalid", False, False), ("semantic-invalid", True, False)):
        paths = sorted((PROFILE / "fixtures" / group).glob("*.json"))
        assert paths, group
        counts[group] = len(paths)
        for path in paths:
            payload = load(path)
            errors = list(validator.iter_errors(payload))
            assert (not errors) == structural, (path, errors)
            if structural:
                issues = payload_issues(payload)
                assert (not issues) == semantic, (path, issues)
    payload = load(PROFILE / "fixtures" / "valid" / "shared-entry.json")
    document = make_document(payload)
    assert not list(core.iter_errors(document))
    declarations = {d["symbol"]: d for d in document["semanticModels"][0]["declarations"]}
    assert not payload_issues(payload, declarations)
    swapped_role = copy.deepcopy(payload)
    swapped_role["yield"]["members"][0]["role"] = "value"
    assert "entry member role must match its exact source projection" in payload_issues(swapped_role)
    assert not document_issues(document)
    partial = copy.deepcopy(payload)
    partial["construction"]["validity"] = {"kind": "unsupported", "limitation": {"kind": "unsupported-semantics"}}
    assert uncertain(partial) and not list(validator.iter_errors(partial))
    assert list(core.iter_errors(make_document(partial, "partial"))) == []
    partial_document = make_document(partial, "partial")
    assert not document_issues(partial_document)
    invalid_complete = make_document(partial)
    assert "complete scope contains uncertainty or conflict" in document_issues(invalid_complete)
    missing_affects = copy.deepcopy(document)
    missing_affects["semanticModels"][0]["vocabularyUses"][0]["affects"][0]["scope"]["resume"] = "other"
    assert "fact absent from exact affects" in document_issues(missing_affects)
    assert independent_yields(payload, {"k1": "v1", "k2": "v2"}) == [("k1", "v1"), ("k2", "v2")]
    assert independent_yields(payload, {}) == []
    print(
        f"deferred yield: {counts}, one valid complete document, one valid partial document, "
        "two cross-record semantic rejections, repeated and empty consumer cases passed"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
