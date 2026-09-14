#!/usr/bin/env python3
"""Build the bounded CSMI runtime-values 0.2 conformance corpus.

The fixture producer reuses the repository validator's canonicalization and
therefore requires requirements-validation.txt, including jsonschema. It is also
importable by the semantic validator: ``make_documents`` returns the
complete-document cases and ``make_raw_payloads`` returns payload cases.
Digest inputs use the validator's RFC 8785-compatible canonicalizer.
Runtime-values arrays are semantic sets, so array members are normalized and
sorted before serialization.  The corpus uses only integer offsets and
deterministic ASCII source, avoiding implementation-dependent JSON or byte
encodings.  ``--check`` verifies checked-in bytes without rewriting them.
"""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import sys
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles" / "runtime-values" / "0.2"
SCHEMA_URI = "https://csmi.brokk.ai/schema/profiles/runtime-values/0.2/schema.json"
CORE_SCHEMA_URI = "https://csmi.brokk.ai/schema/0.1/schema.json"
VOCABULARY = "csmi.runtime-values"
VERSION = "0.2.0"
PRODUCER = "https://csmi.brokk.ai/conformance/runtime-values-0.2"
REVIEWER = PRODUCER + "/reviewer"
POLICY_URI = PRODUCER + "/policy"
PURPOSE_URI = PRODUCER + "/purpose/activation"
NODE_CONTEXT = "https://csmi.brokk.ai/runtime-context/node"
PYTHON_CONTEXT = "https://csmi.brokk.ai/runtime-context/cpython"
EXACT_STRING = "https://csmi.brokk.ai/key-equality/exact-string"
EXACT_INDEX = "https://csmi.brokk.ai/key-equality/exact-index"
PLATFORM_DEFINED = "https://csmi.brokk.ai/key-equality/platform-defined"

FAMILIES = (
    "runtime-contracts",
    "runtime-targets",
    "runtime-activations",
    "runtime-bindings",
    "runtime-observations",
)

# Public fixture expectations consumed by focused tests and downstream
# producers.  These are semantic outcomes, not a priority ordering.
EXPECTED_ACTIVATION_OUTCOMES = {
    "portable-node-env": "matched",
    "argv": "matched",
    "artifact-specialization": "matched",
    "unknown-target": "indeterminate",
    "conflict": "conflict",
    "unsupported-context": "unsupported",
    "partial-target-range": "indeterminate",
    "mixed-node-browser": "matched",
    "windows-main-unknown-equality": "matched",
    "worker-copy": "matched",
    "worker-shared": "matched",
    "written": "matched",
    "deleted": "matched",
    "dynamic": "matched",
    "shadowed": "matched",
    "inherited": "matched",
    "proxy": "matched",
    "open-effects": "matched",
    "python-env": "matched",
    "complete-proof": "matched",
}


def canonical_json(value: Any) -> str:
    """Compact UTF-8 JSON after profile semantic-set normalization."""

    return _validator_canonical(value).decode("utf-8")


def digest(value: Any) -> str:
    return _validator_digest(value)


def text_digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


_VALIDATOR: Any | None = None


def _validator() -> Any:
    global _VALIDATOR
    if _VALIDATOR is None:
        path = ROOT / "scripts" / "validate-runtime-values-0.2.py"
        spec = importlib.util.spec_from_file_location("runtime_values_validator_02", path)
        if spec is None or spec.loader is None:
            raise RuntimeError(f"cannot import validator at {path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        _VALIDATOR = module
    return _VALIDATOR


def _validator_canonical(value: Any) -> bytes:
    return _validator().canonical(value)


def _validator_digest(value: Any) -> str:
    return _validator().digest(value)


def _evidence(method: str, *inputs: Any) -> dict[str, Any]:
    material = {"method": method, "inputs": list(inputs)}
    return {
        "producer": PRODUCER,
        "method": method,
        "inputsDigest": digest(material),
    }


def _scheme(identifier: str) -> dict[str, str]:
    return {"identifier": identifier, "version": VERSION}


def _coverage(status: str, *limitations: str) -> dict[str, Any]:
    result: dict[str, Any] = {"status": status}
    if status != "complete":
        result["limitations"] = list(dict.fromkeys(limitations))
    return result


def _selector(purl: str, version_range: str | None = None, artifact: str | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {"purl": purl}
    if version_range is not None:
        result["versionRange"] = version_range
    if artifact is not None:
        result["digests"] = [{
            "algorithm": "sha-256",
            "coverage": "conformance-synthetic-artifact-bytes",
            "canonicalization": "https://csmi.brokk.ai/canonicalization/raw-utf8-v1",
            "value": artifact,
        }]
    return result


def _context_constraints(
    scheme: str,
    *,
    platforms: tuple[str, ...] = ("linux", "darwin"),
    realms: tuple[str, ...] = ("main", "worker-copy", "worker-shared"),
    module_modes: tuple[str, ...] = ("commonjs", "esm"),
    launch_modes: tuple[str, ...] = ("script", "eval", "stdin", "repl", "worker"),
    boundaries: tuple[str, ...] = ("runtime-entry", "application-entry"),
) -> dict[str, Any]:
    return {
        "scheme": _scheme(scheme),
        "platform": list(platforms),
        "architecture": ["x64"],
        "realm": list(realms),
        "moduleMode": list(module_modes),
        "launchMode": list(launch_modes),
        "initializationBoundary": list(boundaries),
    }


def _context(
    scheme: str,
    platform: str,
    realm: str,
    module_mode: str,
    launch_mode: str,
    boundary: str,
) -> dict[str, Any]:
    return {
        "scheme": _scheme(scheme),
        "platform": platform,
        "architecture": "x64",
        "realm": realm,
        "moduleMode": module_mode,
        "launchMode": launch_mode,
        "initializationBoundary": boundary,
    }


def _surface(container: str, root: str = "https://csmi.brokk.ai/runtime-root/node-process") -> dict[str, str]:
    return {"root": root, "container": container}


def _behavior(
    *,
    key_domain: str = "static-property",
    lookup: str = "own-value",
    absent: str = "undefined",
    equality: str = EXACT_STRING,
    exceptions: str = "may-throw",
    materialization: str = "host-defined",
    conversion: str = "string-conversion",
    normal_write: str = "store-converted-value",
    exceptional_write: str = "may-mutate",
    normal_delete: str = "remove-entry",
    exceptional_delete: str = "may-mutate",
    origins: list[dict[str, Any]] | None = None,
    coverage: dict[str, Any] | None = None,
) -> dict[str, Any]:
    if origins is None:
        origins = [{"keys": {"kind": "all-properties"}, "origin": "external-environment"}]
    if coverage is None:
        coverage = _coverage("partial", "exception-behavior-indeterminate", "materialization-incomplete")
    return {
        "keyDomain": key_domain,
        "lookup": lookup,
        "presentValue": "string",
        "absent": absent,
        "keyEquality": _scheme(equality),
        "read": {"exceptions": exceptions, "materialization": materialization},
        "write": {
            "conversion": conversion,
            "normal": normal_write,
            "exceptional": exceptional_write,
        },
        "delete": {"normal": normal_delete, "exceptional": exceptional_delete},
        "initialOrigins": origins,
        "coverage": coverage,
    }


def contract_definition(
    contract_id: str,
    *,
    identifier: str,
    selector: dict[str, Any],
    context: dict[str, Any],
    surface: dict[str, str],
    languages: list[str],
    assumptions: list[str],
    behavior: dict[str, Any],
) -> dict[str, Any]:
    """Build and return the digest input for a runtime contract."""

    del contract_id  # the local inventory ID is intentionally not semantic content
    return {
        "identifier": identifier,
        "version": VERSION,
        "applicability": {
            "basis": "portable" if "digests" not in selector else "artifact-specific",
            "selectors": [selector],
        },
        "context": context,
        "surface": surface,
        "languages": languages,
        "assumptions": assumptions,
        "behavior": behavior,
    }


def contract(
    contract_id: str,
    *,
    identifier: str,
    selector: dict[str, Any],
    context: dict[str, Any],
    surface: dict[str, str],
    languages: list[str],
    assumptions: list[str],
    behavior: dict[str, Any],
) -> dict[str, Any]:
    definition = contract_definition(
        contract_id,
        identifier=identifier,
        selector=selector,
        context=context,
        surface=surface,
        languages=languages,
        assumptions=assumptions,
        behavior=behavior,
    )
    return {
        "kind": "runtime-contract",
        "contractId": contract_id,
        "definition": definition,
        "contractDigest": digest(definition),
        "evidence": _evidence("synthetic-contract-review", contract_id, definition),
    }


def _source(name: str, text: str) -> tuple[str, str, dict[str, Any]]:
    resource = f"conformance://runtime-values-0.2/source/{name}"
    resource_digest = text_digest(text)
    return resource, resource_digest, {
        "resource": resource,
        "resourceDigest": resource_digest,
    }


def _target(
    target_id: str,
    *,
    partition: str,
    resource: dict[str, Any],
    runtime: dict[str, Any] | None,
    context: dict[str, Any],
    basis: str = "declared-target",
    coverage: dict[str, Any] | None = None,
    assumptions: list[str] | None = None,
) -> dict[str, Any]:
    definition: dict[str, Any] = {
        "partition": partition,
        "resources": [resource],
        "basis": basis,
        "context": context,
        "assumptions": assumptions or [
            PRODUCER + "/assumption/synthetic-source-closure",
            PRODUCER + "/assumption/host-runtime-input",
            PRODUCER + "/assumption/import-time-mapping",
            PRODUCER + "/assumption/verified-synthetic-artifact",
            PRODUCER + "/assumption/conflict-a",
            PRODUCER + "/assumption/conflict-b",
        ],
        "evidence": _evidence("synthetic-declared-target", target_id, partition, resource),
        "coverage": coverage or _coverage("complete"),
    }
    if runtime is not None:
        definition["runtime"] = runtime
    return {
        "kind": "runtime-target",
        "targetId": target_id,
        "definition": definition,
        "targetDigest": digest(definition),
    }


def _policy(target: dict[str, Any], contracts: list[dict[str, Any]]) -> dict[str, Any]:
    inputs = {"target": target["targetDigest"], "contracts": contracts}
    return {
        "identifier": POLICY_URI,
        "version": VERSION,
        "inputsDigest": digest(inputs),
        "trustedReviewers": [REVIEWER],
        "purpose": PURPOSE_URI,
    }


def activation_input(
    activation: dict[str, Any],
    contracts: dict[str, dict[str, Any]],
    targets: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    """Return the exact activation semantic digest object used by the validator."""

    return {
        "targetDigest": targets[activation["targetId"]]["targetDigest"],
        "surface": activation["surface"],
        "contracts": [contracts[name] for name in activation["candidateIds"]],
        **{name: activation[name] for name in (
            "candidateCoverage", "disabledIds", "reviews", "policy", "outcome", "selectedIds"
        )},
    }


def _activation(
    activation_id: str,
    *,
    target: dict[str, Any],
    surface: dict[str, str],
    contracts: list[dict[str, Any]],
    outcome: str,
    selected_ids: list[str],
    disabled_ids: list[str] | None = None,
    candidate_coverage: dict[str, Any] | None = None,
    reviews: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    disabled_ids = disabled_ids or []
    candidate_coverage = candidate_coverage or _coverage("complete")
    if reviews is None:
        reviews = [
            {
                "contractDigest": item["contractDigest"],
                "targetDigest": target["targetDigest"],
                "purpose": PURPOSE_URI,
                "reviewer": REVIEWER,
                "decision": "approved",
                "evidence": _evidence("synthetic-scoped-review", item["contractId"], target["targetId"]),
            }
            for item in contracts
        ]
    policy = _policy(target, contracts)
    result = {
        "kind": "runtime-activation",
        "activationId": activation_id,
        "targetId": target["targetId"],
        "surface": surface,
        "candidateIds": [item["contractId"] for item in contracts],
        "candidateCoverage": candidate_coverage,
        "disabledIds": disabled_ids,
        "reviews": reviews,
        "policy": policy,
        "outcome": outcome,
        "selectedIds": selected_ids,
    }
    result["activationDigest"] = digest(activation_input(
        result,
        {item["contractId"]: item for item in contracts},
        {target["targetId"]: target},
    ))
    return result


def _identity(owner: str, kind: str, locator: Any) -> dict[str, Any]:
    scheme = {"identifier": PRODUCER + "/synthetic-locator", "version": VERSION}
    commitment = {"scheme": scheme, "kind": kind, "locator": locator}
    return {"scheme": scheme, "ownerDigest": owner, "locatorDigest": digest(commitment), "kind": kind}


def _binding(
    binding_id: str,
    *,
    activation: dict[str, Any],
    contract_id: str,
    language: str,
    source_resource: str,
    resource_digest: str,
    lexical: str = "absent",
    rebinding: str = "excluded",
    outcome: str = "exact",
    coverage: dict[str, Any] | None = None,
    source_start: int = 0,
    source_end: int = 1,
) -> dict[str, Any]:
    scope = _identity(resource_digest, "scope", binding_id + ":scope")
    root = _identity(resource_digest, "value", binding_id + ":root")
    container = _identity(resource_digest, "value", binding_id + ":container")
    source = {
        "resource": source_resource,
        "resourceDigest": resource_digest,
        "startByte": source_start,
        "endByte": source_end,
    }
    return {
        "kind": "runtime-binding",
        "bindingId": binding_id,
        "activationId": activation["activationId"],
        "activationDigest": activation["activationDigest"],
        "contractId": contract_id,
        "language": language,
        "source": source,
        "scope": scope,
        "root": root,
        "container": container,
        "lexicalBinding": lexical,
        "rebinding": rebinding,
        "outcome": outcome,
        "evidence": _evidence("synthetic-resolver-binding", binding_id, resource_digest),
        "coverage": coverage or _coverage("complete"),
    }


def _observation(
    observation_id: str,
    *,
    binding: dict[str, Any],
    target: dict[str, Any],
    source_resource: str,
    source_digest: str,
    start: int,
    end: int,
    key: dict[str, Any],
    source_form: str,
    relationship: str,
    origin: str,
    proof_values: dict[str, str],
    coverage: dict[str, Any],
    storage_key: dict[str, Any] | None = None,
    phase: str = "after-effects",
) -> dict[str, Any]:
    source = {
        "resource": source_resource,
        "resourceDigest": source_digest,
        "startByte": start,
        "endByte": end,
    }
    # The loaded container is the binding's exact semantic value identity.
    # The other value/operation/point identities are occurrence-owned.
    base = binding["container"]
    load = _identity(source_digest, "operation", observation_id + ":load")
    result = _identity(source_digest, "value", observation_id + ":result")
    point = _identity(source_digest, "point", observation_id + ":point")
    container = binding["container"]
    store = {
        "invocation": _identity(target["targetDigest"], "invocation", target["targetId"] + ":invocation"),
        "realm": _identity(target["targetDigest"], "realm", target["targetId"] + ":realm"),
        "container": container,
        "backing": _identity(target["targetDigest"], "store", target["targetId"] + ":backing"),
        "relationship": relationship,
        "evidence": _evidence("synthetic-store-identity", observation_id, target["targetDigest"]),
    }
    if relationship == "copied":
        store["copiedFrom"] = _identity(target["targetDigest"], "store", target["targetId"] + ":source-store")
        store["copyPoint"] = _identity(source_digest, "point", observation_id + ":copy")
    if key.get("kind") in {"dynamic", "unsupported"}:
        proof_values = {**proof_values, "keyNormalization": "unknown"}
    elif proof_values.get("keyNormalization", "exact") == "exact" and storage_key is None:
        storage_key = copy.deepcopy(key)
    proof_without_digest = {
        "initialization": proof_values["initialization"],
        "dependencies": proof_values["dependencies"],
        "mutation": proof_values["mutation"],
        "lookup": proof_values["lookup"],
        "materialization": proof_values["materialization"],
        "normal": proof_values["normal"],
        "exceptional": proof_values["exceptional"],
        "keyNormalization": proof_values.get("keyNormalization", "exact"),
    }
    proof = {
        **proof_without_digest,
        "evidence": _evidence("synthetic-observation-proof", observation_id, proof_without_digest),
    }
    proof["closureDigest"] = digest(proof)
    return {
        "kind": "runtime-observation",
        "observationId": observation_id,
        "bindingId": binding["bindingId"],
        "key": key,
        **({"storageKey": storage_key} if storage_key is not None else {}),
        "sourceForm": source_form,
        "source": source,
        "baseValue": base,
        "loadOperation": load,
        "resultValue": result,
        "point": point,
        "phase": phase,
        "store": store,
        "origin": origin,
        "proof": proof,
        "coverage": coverage,
    }


def _fact(family: str, identity_field: str, payload: dict[str, Any]) -> dict[str, Any]:
    identity = payload[identity_field]
    return {
        "vocabulary": VOCABULARY,
        "version": VERSION,
        "family": family,
        "scope": {identity_field: identity},
        "payload": payload,
        "provenance": ["runtime-values-conformance"],
    }


def _document_models(
    *,
    contract_records: list[dict[str, Any]],
    target: dict[str, Any],
    activation: dict[str, Any],
    binding: dict[str, Any] | list[dict[str, Any]],
    observations: list[dict[str, Any]],
    artifact_selectors: list[dict[str, Any]],
    extra_model: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    contract_facts = [_fact("runtime-contracts", "contractId", record) for record in contract_records]
    target_fact = _fact("runtime-targets", "targetId", target)
    activation_fact = _fact("runtime-activations", "activationId", activation)
    binding_records = binding if isinstance(binding, list) else [binding]
    binding_fact = [_fact("runtime-bindings", "bindingId", item) for item in binding_records]
    observation_facts = [_fact("runtime-observations", "observationId", item) for item in observations]
    all_facts = contract_facts + [target_fact, activation_fact] + binding_fact + observation_facts
    affected = [
        {"kind": "fact-family", "family": fact["family"], "scope": fact["scope"]}
        for fact in all_facts
    ]
    model: dict[str, Any] = {
        "artifactSelectors": artifact_selectors,
        "vocabularyUses": [{
            "identifier": VOCABULARY,
            "version": VERSION,
            "schema": SCHEMA_URI,
            "requirement": "required",
            "affects": affected,
        }],
        "extensionFacts": all_facts,
    }
    result = [model]
    if extra_model is not None:
        result.append(extra_model)
    return result


def _document(models: list[dict[str, Any]], *, name: str) -> dict[str, Any]:
    del name
    return {
        "documentType": "semantic-document",
        "schema": CORE_SCHEMA_URI,
        "semanticModelVersion": "0.1",
        "serializationVersion": "0.1-json",
        "provenanceRecords": [{
            "id": "runtime-values-conformance",
            "producer": {"identifier": PRODUCER, "version": VERSION},
            "generationMethod": "manual-authoring",
        }],
        "defaultProvenance": "runtime-values-conformance",
        "semanticModels": models,
    }


def _node_case(
    name: str,
    *,
    container: str = "env",
    target_context: dict[str, Any] | None = None,
    target_runtime: dict[str, Any] | None | str = "default",
    target_basis: str = "declared-target",
    target_coverage: dict[str, Any] | None = None,
    contract_records: list[dict[str, Any]] | None = None,
    contract_context: dict[str, Any] | None = None,
    contract_selector: dict[str, Any] | None = None,
    behavior: dict[str, Any] | None = None,
    activation_outcome: str = "matched",
    selected: list[str] | None = None,
    binding_outcome: str = "exact",
    lexical: str = "absent",
    rebinding: str = "excluded",
    binding_coverage: dict[str, Any] | None = None,
    observation_id: str | None = None,
    key: dict[str, Any] | None = None,
    source_form: str = "dot",
    origin: str = "initial-if-present",
    proof_values: dict[str, str] | None = None,
    observation_coverage: dict[str, Any] | None = None,
    relationship: str = "isolated",
    realm: str = "main",
    artifact_selector: dict[str, Any] | None = None,
    source_text: str | None = None,
) -> dict[str, Any]:
    contract_id = "node-env-portable"
    source_text = source_text or f"// synthetic {name}\nprocess.env.CONFIG_TOKEN;\n"
    source_resource, source_digest, resource = _source(name, source_text)
    if contract_selector is None:
        contract_selector = _selector(
            "pkg:generic/nodejs.org/node",
            "vers:semver/>=22.11.0|<23.0.0",
        )
    if contract_context is None:
        contract_context = _context_constraints(NODE_CONTEXT)
    if behavior is None:
        behavior = _behavior()
    if contract_records is None:
        contract_records = [contract(
            contract_id,
            identifier="https://csmi.brokk.ai/runtime-contract/node-process-env",
            selector=contract_selector,
            context=contract_context,
            surface=_surface(container),
            languages=["javascript", "typescript", "tsx"],
            assumptions=[PRODUCER + "/assumption/host-runtime-input"],
            behavior=behavior,
        )]
    if target_runtime == "default":
        target_runtime = _selector("pkg:generic/nodejs.org/node@22.11.0")
    if target_context is None:
        target_context = _context(NODE_CONTEXT, "linux", realm, "commonjs", "script", "runtime-entry")
    target_id = name + "-target"
    target = _target(
        target_id,
        partition=f"conformance://runtime-values-0.2/partition/{name}",
        resource=resource,
        runtime=target_runtime,
        context=target_context,
        basis=target_basis,
        coverage=target_coverage,
    )
    surface = _surface(container)
    activation = _activation(
        name + "-activation",
        target=target,
        surface=surface,
        contracts=contract_records,
        outcome=activation_outcome,
        selected_ids=selected if selected is not None else ([contract_id] if activation_outcome == "matched" else []),
    )
    binding = _binding(
        name + "-binding",
        activation=activation,
        contract_id=contract_records[0]["contractId"],
        language="javascript",
        source_resource=source_resource,
        resource_digest=source_digest,
        lexical=lexical,
        rebinding=rebinding,
        outcome=binding_outcome,
        coverage=binding_coverage,
    )
    if observation_id is None:
        observation_id = name + "-observation"
    if key is None:
        key = {"kind": "property", "value": "CONFIG_TOKEN"}
    if proof_values is None:
        proof_values = {
            "initialization": "closed",
            "dependencies": "closed",
            "mutation": "pristine",
            "lookup": "own-present",
            "materialization": "resolved",
            "normal": "exact",
            "exceptional": "modeled",
        }
    if behavior["keyEquality"]["identifier"] == PLATFORM_DEFINED and proof_values.get("keyNormalization") is None:
        proof_values = {**proof_values, "keyNormalization": "unknown"}
    if observation_coverage is None:
        observation_coverage = _coverage("partial", "exception-behavior-indeterminate", "materialization-incomplete")
    observation = _observation(
        observation_id,
        binding=binding,
        target=target,
        source_resource=source_resource,
        source_digest=source_digest,
        start=0,
        end=len(source_text.encode("utf-8")),
        key=key,
        source_form=source_form,
        relationship=relationship,
        origin=origin,
        proof_values=proof_values,
        coverage=observation_coverage,
    )
    models = _document_models(
        contract_records=contract_records,
        target=target,
        activation=activation,
        binding=binding,
        observations=[observation],
        artifact_selectors=artifact_selector and [artifact_selector] or [contract_selector],
    )
    return _document(models, name=name)


def _argv_document() -> dict[str, Any]:
    name = "argv"
    source_text = "// synthetic argv\nprocess.argv[0]; process.argv[1]; process.argv[7];\n"
    source_resource, source_digest, resource = _source(name, source_text)
    selector = _selector("pkg:generic/nodejs.org/node", "vers:semver/>=22.11.0|<23.0.0")
    argv_behavior = _behavior(
        key_domain="static-index",
        absent="undefined",
        equality=EXACT_INDEX,
        conversion="identity",
        origins=[
            {"keys": {"kind": "index-range", "minimum": 0, "maximum": 0}, "origin": "executable-path"},
            {"keys": {"kind": "index-range", "minimum": 1, "maximum": 1}, "origin": "entry-path"},
            {"keys": {"kind": "index-range", "minimum": 2, "maximum": 4294967294}, "origin": "application-argument"},
        ],
    )
    argv_contract = contract(
        "node-argv-portable",
        identifier="https://csmi.brokk.ai/runtime-contract/node-process-argv",
        selector=selector,
        context=_context_constraints(NODE_CONTEXT, platforms=("linux", "darwin", "windows"), realms=("main",), module_modes=("commonjs", "esm"), launch_modes=("script",), boundaries=("runtime-entry", "application-entry")),
        surface=_surface("argv"),
        languages=["javascript", "typescript", "tsx"],
        assumptions=[PRODUCER + "/assumption/host-runtime-input"],
        behavior=argv_behavior,
    )
    target = _target(
        "argv-target",
        partition="conformance://runtime-values-0.2/partition/argv",
        resource=resource,
        runtime=_selector("pkg:generic/nodejs.org/node@22.11.0"),
        context=_context(NODE_CONTEXT, "linux", "main", "commonjs", "script", "runtime-entry"),
    )
    activation = _activation("argv-activation", target=target, surface=_surface("argv"), contracts=[argv_contract], outcome="matched", selected_ids=["node-argv-portable"])
    binding = _binding("argv-binding", activation=activation, contract_id="node-argv-portable", language="javascript", source_resource=source_resource, resource_digest=source_digest)
    observations = []
    bindings = []
    for index in (0, 1, 7):
        marker = f"process.argv[{index}]"
        start = source_text.index(marker)
        end = start + len(marker.encode("utf-8"))
        current_binding = _binding(f"argv-binding-{index}", activation=activation, contract_id="node-argv-portable", language="javascript", source_resource=source_resource, resource_digest=source_digest, source_start=start, source_end=end)
        bindings.append(current_binding)
        observations.append(_observation(
            f"argv-index-{index}",
            binding=current_binding,
            target=target,
            source_resource=source_resource,
            source_digest=source_digest,
            start=start,
            end=end,
            key={"kind": "index", "value": index},
            source_form="bracket-number",
            relationship="isolated",
            origin="initial-if-present",
            proof_values={
                "initialization": "closed", "dependencies": "closed", "mutation": "pristine",
                "lookup": "own-present", "materialization": "resolved", "normal": "exact", "exceptional": "modeled",
            },
            coverage=_coverage("partial", "exception-behavior-indeterminate", "materialization-incomplete"),
        ))
    model = _document_models(
        contract_records=[argv_contract], target=target, activation=activation,
        binding=bindings, observations=observations, artifact_selectors=[selector],
    )
    return _document(model, name=name)


def _python_document() -> dict[str, Any]:
    name = "python-env"
    source_text = "# synthetic python env\nos.environ['CONFIG_TOKEN']\n"
    source_resource, source_digest, resource = _source(name, source_text)
    selector = _selector("pkg:generic/python.org/cpython", "vers:pypi/>=3.13.0|<3.14.0")
    python_contract = contract(
        "cpython-os-environ-portable",
        identifier="https://csmi.brokk.ai/runtime-contract/cpython-os-environ",
        selector=selector,
        context=_context_constraints(PYTHON_CONTEXT, realms=("main",), module_modes=("python",), launch_modes=("script", "module", "command", "stdin", "repl"), boundaries=("module-import", "application-entry")),
        surface=_surface("environ", "https://csmi.brokk.ai/runtime-root/python-os"),
        languages=["python"],
        assumptions=[PRODUCER + "/assumption/import-time-mapping"],
        behavior=_behavior(
            lookup="mapping-entry",
            absent="exception",
            equality=EXACT_STRING,
            exceptions="may-throw",
            materialization="host-defined",
            conversion="requires-contract",
        ),
    )
    target = _target(
        "python-env-target",
        partition="conformance://runtime-values-0.2/partition/python-env",
        resource=resource,
        runtime=_selector("pkg:generic/python.org/cpython@3.13.0"),
        context=_context(PYTHON_CONTEXT, "linux", "main", "python", "script", "module-import"),
    )
    surface = _surface("environ", "https://csmi.brokk.ai/runtime-root/python-os")
    activation = _activation("python-env-activation", target=target, surface=surface, contracts=[python_contract], outcome="matched", selected_ids=[python_contract["contractId"]])
    binding = _binding("python-env-binding", activation=activation, contract_id=python_contract["contractId"], language="python", source_resource=source_resource, resource_digest=source_digest, source_start=27, source_end=len(source_text.encode("utf-8")))
    observation = _observation(
        "python-env-observation", binding=binding, target=target,
        source_resource=source_resource, source_digest=source_digest,
        start=27, end=len(source_text.encode("utf-8")), key={"kind": "property", "value": "CONFIG_TOKEN"},
        source_form="mapping", relationship="isolated", origin="initial-if-present",
        proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "mapping-present", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"},
        coverage=_coverage("partial", "exception-behavior-indeterminate", "materialization-incomplete"),
    )
    return _document(_document_models(contract_records=[python_contract], target=target, activation=activation, binding=binding, observations=[observation], artifact_selectors=[selector]), name=name)


def _complete_proof_document() -> dict[str, Any]:
    """A separately synthetic, fully closed proof used to test completeness."""

    return _node_case(
        "complete-proof",
        source_text="// explicitly synthetic closed host\nprocess.env.CONFIG_TOKEN;\n",
        behavior=_behavior(
            exceptions="nonthrowing", materialization="eager", exceptional_write="unchanged", exceptional_delete="unchanged",
            coverage=_coverage("complete"),
        ),
        observation_coverage=_coverage("complete"),
        proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "own-present", "materialization": "resolved", "normal": "exact", "exceptional": "excluded"},
    )


def _mixed_document() -> dict[str, Any]:
    """Keep Node and browser partitions as separate semantic models."""

    node = _node_case("mixed-node-browser-node")
    browser_text = "// synthetic browser partition\nwindow.location.href;\n"
    source_resource, source_digest, resource = _source("mixed-node-browser-browser", browser_text)
    # The browser record is an explicit non-applicable Node candidate.  It
    # remains in the browser partition to prove that it was considered, but
    # does not create a browser runtime binding.
    selector = _selector("pkg:generic/web/browser@1.0.0")
    node_contract = contract(
        "node-env-browser-candidate",
        identifier="https://csmi.brokk.ai/runtime-contract/node-process-env-browser-candidate",
        selector=selector,
        context=_context_constraints("https://csmi.brokk.ai/runtime-context/browser", platforms=("linux", "darwin", "windows"), realms=("main",), module_modes=("esm",), launch_modes=("script",), boundaries=("runtime-entry",)),
        surface=_surface("env"),
        languages=["javascript"],
        assumptions=[PRODUCER + "/assumption/host-runtime-input"],
        behavior=_behavior(),
    )
    target = _target(
        "mixed-browser-target", partition="conformance://runtime-values-0.2/partition/mixed-browser",
        resource=resource, runtime=_selector("pkg:generic/web/browser@1.0.0"),
        context=_context(NODE_CONTEXT, "linux", "main", "esm", "script", "runtime-entry"),
    )
    activation = _activation("mixed-browser-activation", target=target, surface=_surface("env"), contracts=[node_contract], outcome="unsupported", selected_ids=[])
    binding = _binding("mixed-browser-binding", activation=activation, contract_id=node_contract["contractId"], language="javascript", source_resource=source_resource, resource_digest=source_digest, outcome="indeterminate", coverage=_coverage("partial", "activation-missing"))
    observation = _observation(
        "mixed-browser-observation", binding=binding, target=target,
        source_resource=source_resource, source_digest=source_digest, start=0, end=len(browser_text.encode("utf-8")),
        key={"kind": "unsupported"}, source_form="unsupported", relationship="isolated", origin="unknown",
        proof_values={"initialization": "unknown", "dependencies": "unknown", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"},
        coverage=_coverage("unknown", "activation-missing"),
    )
    browser_model = _document_models(contract_records=[node_contract], target=target, activation=activation, binding=binding, observations=[observation], artifact_selectors=[_selector("pkg:generic/web/browser@1.0.0")])[0]
    return _document(node["semanticModels"] + [browser_model], name="mixed-node-browser")


def make_documents() -> dict[str, dict[str, Any]]:
    """Return all structurally valid complete-document conformance cases."""

    docs: dict[str, dict[str, Any]] = {
        "portable-node-env": _node_case("portable-node-env"),
        "argv": _argv_document(),
        "artifact-specialization": None,  # filled below for readability
        "unknown-target": _node_case(
            "unknown-target",
            target_runtime=None,
            target_basis="unknown",
            target_coverage=_coverage("partial", "target-unknown"),
            # Unknown target coverage must remain non-complete.
            # _node_case forwards this as target evidence below.
            target_context=_context(NODE_CONTEXT, "unknown", "unknown", "unknown", "unknown", "unknown"),
            activation_outcome="indeterminate", binding_outcome="indeterminate",
            binding_coverage=_coverage("partial", "target-unknown", "activation-missing"),
            observation_coverage=_coverage("unknown", "target-unknown", "activation-missing"),
            proof_values={"initialization": "unknown", "dependencies": "unknown", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"},
            origin="unknown",
        ),
        "conflict": None,
        "unsupported-context": _node_case(
            "unsupported-context",
            target_context=_context("https://csmi.brokk.ai/runtime-context/unsupported", "linux", "main", "commonjs", "script", "runtime-entry"),
            activation_outcome="unsupported", binding_outcome="unsupported",
            binding_coverage=_coverage("partial", "activation-unsupported"), observation_coverage=_coverage("unknown", "activation-unsupported"),
            proof_values={"initialization": "unknown", "dependencies": "unknown", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"}, origin="unknown",
        ),
        "partial-target-range": _node_case(
            "partial-target-range",
            target_runtime=_selector("pkg:generic/nodejs.org/node", "vers:semver/>=22.11.0|<24.0.0"),
            activation_outcome="indeterminate", binding_outcome="indeterminate",
            binding_coverage=_coverage("partial", "coverage-limited"), observation_coverage=_coverage("unknown", "coverage-limited"),
            proof_values={"initialization": "unknown", "dependencies": "unknown", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"}, origin="unknown",
        ),
        "mixed-node-browser": None,
        "windows-main-unknown-equality": _node_case(
            "windows-main-unknown-equality",
            target_context=_context(NODE_CONTEXT, "windows", "main", "commonjs", "script", "runtime-entry"),
            contract_context=_context_constraints(NODE_CONTEXT, platforms=("linux", "darwin", "windows")),
            behavior=_behavior(equality=PLATFORM_DEFINED, coverage=_coverage("partial", "equality-unknown", "exception-behavior-indeterminate", "materialization-incomplete")),
            observation_coverage=_coverage("partial", "equality-unknown", "exception-behavior-indeterminate"),
            proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "own-present", "materialization": "resolved", "normal": "exact", "exceptional": "modeled", "keyNormalization": "unknown"},
        ),
        "worker-copy": _node_case(
            "worker-copy", realm="worker-copy",
            target_context=_context(NODE_CONTEXT, "linux", "worker-copy", "commonjs", "worker", "runtime-entry"),
            relationship="copied",
        ),
        "worker-shared": _node_case(
            "worker-shared", realm="worker-shared",
            target_context=_context(NODE_CONTEXT, "linux", "worker-shared", "commonjs", "worker", "runtime-entry"),
            relationship="shared", observation_coverage=_coverage("partial", "sharing-unknown", "exception-behavior-indeterminate"),
        ),
        "written": _node_case(
            "written", proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "written", "lookup": "own-present", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"}, origin="written",
        ),
        "deleted": _node_case(
            "deleted", proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "deleted", "lookup": "absent-no-fallback", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"}, origin="deleted",
        ),
        "dynamic": _node_case(
            "dynamic", key={"kind": "dynamic"}, source_form="unsupported", origin="unknown",
            proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"},
            observation_coverage=_coverage("partial", "dynamic-key", "lookup-incomplete", "materialization-incomplete", "exception-behavior-indeterminate"),
        ),
        "shadowed": _node_case(
            "shadowed", lexical="present", rebinding="excluded", binding_outcome="excluded", origin="unknown",
            binding_coverage=_coverage("complete"),
            proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "unreachable", "exceptional": "excluded"},
            observation_coverage=_coverage("partial", "lookup-incomplete"),
        ),
        "inherited": _node_case(
            "inherited", origin="unknown",
            proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "inherited", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"},
            observation_coverage=_coverage("partial", "lookup-incomplete"),
        ),
        "proxy": _node_case(
            "proxy", origin="unknown",
            proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "proxy", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"},
            observation_coverage=_coverage("partial", "lookup-incomplete", "materialization-incomplete"),
        ),
        "open-effects": _node_case(
            "open-effects", origin="unknown", proof_values={"initialization": "open", "dependencies": "open", "mutation": "unknown", "lookup": "unknown", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"},
            observation_coverage=_coverage("partial", "initialization-incomplete", "coverage-limited"),
        ),
        "python-env": _python_document(),
        "complete-proof": _complete_proof_document(),
    }

    artifact_text = "// synthetic artifact specialization\nprocess.env.CONFIG_TOKEN;\n"
    artifact_resource, artifact_source_digest, _ = _source("artifact-specialization", artifact_text)
    artifact_selector_digest = text_digest("synthetic Node artifact bytes 22.11.0")
    artifact_selector = _selector("pkg:generic/nodejs.org/node@22.11.0", artifact=artifact_selector_digest)
    artifact_contract = contract(
        "node-env-artifact", identifier="https://csmi.brokk.ai/runtime-contract/node-process-env-artifact",
        selector=artifact_selector, context=_context_constraints(NODE_CONTEXT), surface=_surface("env"),
        languages=["javascript", "typescript", "tsx"], assumptions=[PRODUCER + "/assumption/verified-synthetic-artifact"], behavior=_behavior(),
    )
    artifact_target = _target("artifact-specialization-target", partition="conformance://runtime-values-0.2/partition/artifact-specialization", resource={"resource": artifact_resource, "resourceDigest": artifact_source_digest}, runtime=artifact_selector, context=_context(NODE_CONTEXT, "linux", "main", "commonjs", "script", "runtime-entry"))
    artifact_activation = _activation("artifact-specialization-activation", target=artifact_target, surface=_surface("env"), contracts=[artifact_contract], outcome="matched", selected_ids=[artifact_contract["contractId"]])
    artifact_binding = _binding("artifact-specialization-binding", activation=artifact_activation, contract_id=artifact_contract["contractId"], language="javascript", source_resource=artifact_resource, resource_digest=artifact_source_digest)
    artifact_obs = _observation("artifact-specialization-observation", binding=artifact_binding, target=artifact_target, source_resource=artifact_resource, source_digest=artifact_source_digest, start=0, end=len(artifact_text.encode()), key={"kind": "property", "value": "CONFIG_TOKEN"}, source_form="dot", relationship="isolated", origin="initial-if-present", proof_values={"initialization": "closed", "dependencies": "closed", "mutation": "pristine", "lookup": "own-present", "materialization": "resolved", "normal": "exact", "exceptional": "modeled"}, coverage=_coverage("partial", "exception-behavior-indeterminate", "materialization-incomplete"))
    docs["artifact-specialization"] = _document(_document_models(contract_records=[artifact_contract], target=artifact_target, activation=artifact_activation, binding=artifact_binding, observations=[artifact_obs], artifact_selectors=[artifact_selector]), name="artifact-specialization")

    conflict_text = "// synthetic conflicting contracts\nprocess.env.CONFIG_TOKEN;\n"
    conflict_resource, conflict_digest, resource = _source("conflict", conflict_text)
    first = contract("node-env-conflict-a", identifier="https://csmi.brokk.ai/runtime-contract/node-process-env-conflict-a", selector=_selector("pkg:generic/nodejs.org/node", "vers:semver/>=22.11.0|<23.0.0"), context=_context_constraints(NODE_CONTEXT), surface=_surface("env"), languages=["javascript"], assumptions=[PRODUCER + "/assumption/conflict-a"], behavior=_behavior())
    second = contract("node-env-conflict-b", identifier="https://csmi.brokk.ai/runtime-contract/node-process-env-conflict-b", selector=_selector("pkg:generic/nodejs.org/node", "vers:semver/>=22.11.0|<23.0.0"), context=_context_constraints(NODE_CONTEXT), surface=_surface("env"), languages=["javascript"], assumptions=[PRODUCER + "/assumption/conflict-b"], behavior=_behavior(absent="exception", equality=PLATFORM_DEFINED))
    conflict_target = _target("conflict-target", partition="conformance://runtime-values-0.2/partition/conflict", resource=resource, runtime=_selector("pkg:generic/nodejs.org/node@22.11.0"), context=_context(NODE_CONTEXT, "linux", "main", "commonjs", "script", "runtime-entry"))
    conflict_activation = _activation("conflict-activation", target=conflict_target, surface=_surface("env"), contracts=[first, second], outcome="conflict", selected_ids=[])
    conflict_binding = _binding("conflict-binding", activation=conflict_activation, contract_id=first["contractId"], language="javascript", source_resource=conflict_resource, resource_digest=conflict_digest, outcome="indeterminate", coverage=_coverage("partial", "activation-conflict"))
    conflict_obs = _observation("conflict-observation", binding=conflict_binding, target=conflict_target, source_resource=conflict_resource, source_digest=conflict_digest, start=0, end=len(conflict_text.encode()), key={"kind": "property", "value": "CONFIG_TOKEN"}, source_form="dot", relationship="isolated", origin="unknown", proof_values={"initialization": "unknown", "dependencies": "unknown", "mutation": "unknown", "lookup": "unknown", "materialization": "unresolved", "normal": "indeterminate", "exceptional": "unknown"}, coverage=_coverage("unknown", "activation-conflict"))
    docs["conflict"] = _document(_document_models(contract_records=[first, second], target=conflict_target, activation=conflict_activation, binding=conflict_binding, observations=[conflict_obs], artifact_selectors=[_selector("pkg:generic/nodejs.org/node", "vers:semver/>=22.11.0|<23.0.0")]), name="conflict")
    docs["mixed-node-browser"] = _mixed_document()
    return docs


def make_raw_payloads() -> dict[str, dict[str, dict[str, Any]]]:
    """Return standalone profile payload fixtures by structural outcome."""

    documents = make_documents()
    model = documents["portable-node-env"]["semanticModels"][0]
    payloads = {
        family: next(fact["payload"] for fact in model["extensionFacts"] if fact["family"] == family)
        for family in FAMILIES
    }
    valid = {f"{family.removeprefix('runtime-')}-portable": copy.deepcopy(value) for family, value in payloads.items()}
    invalid_portable = copy.deepcopy(payloads["runtime-contracts"])
    invalid_portable["definition"]["applicability"]["selectors"][0]["digests"] = [{
        "algorithm": "sha-256", "coverage": "conformance-synthetic-artifact-bytes", "value": "0" * 64,
    }]
    invalid_index = copy.deepcopy(payloads["runtime-observations"])
    invalid_index["key"] = {"kind": "index", "value": -1}
    invalid_identity = copy.deepcopy(payloads["runtime-bindings"])
    invalid_identity["scope"].pop("scheme", None)
    invalid = {
        "portable-with-digest": invalid_portable,
        "bad-index": invalid_index,
        "missing-identity-scheme": invalid_identity,
    }
    return {"valid": valid, "invalid": invalid}


def make_semantic_invalid_documents() -> dict[str, dict[str, Any]]:
    """Return structurally valid documents with one intentional semantic fault."""

    base = make_documents()["portable-node-env"]
    cases: dict[str, dict[str, Any]] = {}

    wrong_digest = copy.deepcopy(base)
    wrong_digest["semanticModels"][0]["extensionFacts"][0]["payload"]["contractDigest"] = "f" * 64
    cases["wrong-digest"] = _rename_fixture(wrong_digest, "wrong-digest")

    bad_join = copy.deepcopy(base)
    facts = bad_join["semanticModels"][0]["extensionFacts"]
    binding = next(item for item in facts if item["family"] == "runtime-bindings")["payload"]
    binding["activationDigest"] = "e" * 64
    cases["bad-join"] = _rename_fixture(bad_join, "bad-join")

    complete_open = copy.deepcopy(make_documents()["complete-proof"])
    complete_model = complete_open["semanticModels"][0]
    obs = next(item for item in complete_model["extensionFacts"] if item["family"] == "runtime-observations")["payload"]
    obs["proof"]["dependencies"] = "open"
    obs["proof"]["closureDigest"] = digest({name: value for name, value in obs["proof"].items() if name != "closureDigest"})
    obs["coverage"] = _coverage("complete")
    cases["complete-with-open-proof"] = _rename_fixture(complete_open, "complete-with-open-proof")

    wrong_selected = copy.deepcopy(base)
    activation = next(item for item in wrong_selected["semanticModels"][0]["extensionFacts"] if item["family"] == "runtime-activations")["payload"]
    activation["selectedIds"] = []
    _refresh_joins(wrong_selected)
    cases["wrong-selected"] = _rename_fixture(wrong_selected, "wrong-selected")

    outside = copy.deepcopy(base)
    target = next(item for item in outside["semanticModels"][0]["extensionFacts"] if item["family"] == "runtime-targets")["payload"]
    # Keep all digests and joins coherent, but move the source out of the
    # target's declared resource partition.  This isolates the membership
    # invariant instead of merely producing a stale-target-digest error.
    target["definition"]["resources"] = [{
        "resource": "conformance://runtime-values-0.2/source/not-the-observed-resource",
        "resourceDigest": text_digest("synthetic resource outside partition"),
    }]
    _refresh_joins(outside)
    cases["reference-outside-partition"] = _rename_fixture(outside, "reference-outside-partition")

    own_inherited = copy.deepcopy(base)
    observation = next(item for item in own_inherited["semanticModels"][0]["extensionFacts"] if item["family"] == "runtime-observations")["payload"]
    observation["proof"]["lookup"] = "inherited"
    observation["proof"]["closureDigest"] = digest({name: value for name, value in observation["proof"].items() if name != "closureDigest"})
    cases["own-vs-inherited"] = _rename_fixture(own_inherited, "own-vs-inherited")

    # A local alias may use a fresh binding/observation ID, but it still
    # describes the same executable point. Written-origin evidence must not
    # contradict the complete initial-value proof already published there.
    contradictory_alias = copy.deepcopy(make_documents()["complete-proof"])
    alias_model = contradictory_alias["semanticModels"][0]
    alias_binding_fact = copy.deepcopy(next(
        item for item in alias_model["extensionFacts"] if item["family"] == "runtime-bindings"
    ))
    alias_observation_fact = copy.deepcopy(next(
        item for item in alias_model["extensionFacts"] if item["family"] == "runtime-observations"
    ))
    alias_binding_id = "alias-binding"
    alias_observation_id = "alias-observation"
    alias_binding_fact["payload"]["bindingId"] = alias_binding_id
    alias_binding_fact["scope"] = {"bindingId": alias_binding_id}
    alias_observation_fact["payload"]["observationId"] = alias_observation_id
    alias_observation_fact["payload"]["bindingId"] = alias_binding_id
    alias_observation_fact["scope"] = {"observationId": alias_observation_id}
    alias_observation = alias_observation_fact["payload"]
    alias_observation["origin"] = "written"
    alias_observation["proof"]["mutation"] = "written"
    alias_observation["proof"]["closureDigest"] = digest({
        name: value for name, value in alias_observation["proof"].items()
        if name != "closureDigest"
    })
    alias_model["extensionFacts"].extend([alias_binding_fact, alias_observation_fact])
    alias_model["vocabularyUses"][0]["affects"].extend([
        {"kind": "fact-family", "family": alias_binding_fact["family"], "scope": alias_binding_fact["scope"]},
        {"kind": "fact-family", "family": alias_observation_fact["family"], "scope": alias_observation_fact["scope"]},
    ])
    cases["contradictory-alias"] = _rename_fixture(contradictory_alias, "contradictory-alias")

    # Hash equality does not make identities interchangeable across locator
    # schemes. Keep owner/locator digests and the binding container unchanged;
    # only the observation's base-value scheme is altered.
    different_scheme = copy.deepcopy(make_documents()["complete-proof"])
    different_model = different_scheme["semanticModels"][0]
    different_observation = next(
        item for item in different_model["extensionFacts"] if item["family"] == "runtime-observations"
    )["payload"]
    different_observation["baseValue"] = {
        **different_observation["baseValue"],
        "scheme": {
            "identifier": PRODUCER + "/alternate-locator",
            "version": VERSION,
        },
    }
    cases["same-hash-different-scheme"] = _rename_fixture(different_scheme, "same-hash-different-scheme")
    return cases


def _refresh_joins(document: dict[str, Any]) -> None:
    """Recompute dependent target/policy/activation/binding identities."""

    for model in document["semanticModels"]:
        facts = model["extensionFacts"]
        contracts = {
            fact["payload"]["contractId"]: fact["payload"]
            for fact in facts if fact["family"] == "runtime-contracts"
        }
        targets = {
            fact["payload"]["targetId"]: fact["payload"]
            for fact in facts if fact["family"] == "runtime-targets"
        }
        activations = [fact["payload"] for fact in facts if fact["family"] == "runtime-activations"]
        for target in targets.values():
            target["targetDigest"] = digest(target["definition"])
        for activation in activations:
            target = targets[activation["targetId"]]
            candidate_records = [contracts[item] for item in activation["candidateIds"]]
            for review in activation["reviews"]:
                review["targetDigest"] = target["targetDigest"]
            activation["policy"] = _policy(target, candidate_records)
            activation["activationDigest"] = digest(activation_input(activation, contracts, targets))
            for fact in facts:
                if fact["family"] == "runtime-bindings" and fact["payload"]["activationId"] == activation["activationId"]:
                    fact["payload"]["activationDigest"] = activation["activationDigest"]


def _rename_fixture(document: dict[str, Any], name: str) -> dict[str, Any]:
    del name
    return copy.deepcopy(document)


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    output = copy.deepcopy(value)
    output.pop("_fixtureName", None)
    path.write_text(json.dumps(output, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _json_text(value: Any) -> str:
    output = copy.deepcopy(value)
    output.pop("_fixtureName", None)
    return json.dumps(output, indent=2, ensure_ascii=False) + "\n"


def _fixture_outputs() -> dict[Path, Any]:
    docs = make_documents()
    outputs: dict[Path, Any] = {}
    for name, document in docs.items():
        outputs[PROFILE / "fixtures" / "documents" / "valid" / f"{name}.json"] = document
    for name, document in make_semantic_invalid_documents().items():
        outputs[PROFILE / "fixtures" / "documents" / "semantic-invalid" / f"{name}.json"] = document
    for group, payloads in make_raw_payloads().items():
        for name, payload in payloads.items():
            outputs[PROFILE / "fixtures" / group / f"{name}.json"] = payload
    return outputs


def write_fixtures(*, check: bool = False) -> None:
    outputs = _fixture_outputs()
    mismatches: list[str] = []
    for path, value in outputs.items():
        expected = _json_text(value)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != expected:
                mismatches.append(str(path.relative_to(ROOT)))
        else:
            _write_json(path, value)
    if check:
        expected_paths = set(outputs)
        fixture_roots = (
            PROFILE / "fixtures" / "valid",
            PROFILE / "fixtures" / "invalid",
            PROFILE / "fixtures" / "documents" / "valid",
            PROFILE / "fixtures" / "documents" / "semantic-invalid",
        )
        for root in fixture_roots:
            for path in root.glob("*.json"):
                if path not in expected_paths:
                    mismatches.append(str(path.relative_to(ROOT)))
    if mismatches:
        raise SystemExit("fixture regeneration differs: " + ", ".join(mismatches))


if __name__ == "__main__":
    write_fixtures(check="--check" in sys.argv[1:])
    print("runtime-values 0.2 fixtures " + ("are deterministic" if "--check" in sys.argv[1:] else "written"))
