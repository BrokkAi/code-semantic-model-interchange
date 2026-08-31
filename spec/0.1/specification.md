# Code Semantic Model Interchange v0.1

Status: **draft**.

CSMI is a semantic interchange specification for describing selected behavior
of software artifacts in a form that independently implemented analyzers can
interpret consistently.

## 1. Specification architecture

### 1.1 Layers

CSMI separates the meaning of semantic facts from their machine representation.

| Layer | Role |
| --- | --- |
| Semantic model | Analyzer-neutral concepts, their meaning, and conformance obligations. |
| Serialization | A concrete encoding of the semantic model. JSON is the first normative serialization. |
| Structural schema | The machine-readable JSON Schema that constrains a JSON document's shape. |
| Semantic conformance | Requirements that structural validation alone cannot express. |
| Pack | The distributable envelope for semantic models, provenance, and integrity metadata. |
| Transport and registry | Out of scope for v0.1. |

JSON Schema validates structure. It does not define semantic interpretation.
Conformance therefore requires both structural validation and the semantic rules
in this specification.

### 1.2 Normative language

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHALL**, **SHALL NOT**,
**SHOULD**, **SHOULD NOT**, **RECOMMENDED**, **MAY**, and **OPTIONAL** are to be
interpreted as described in [BCP 14](https://www.rfc-editor.org/info/bcp14) when,
and only when, they appear in all capitals.

### 1.3 Terminology

* **CSMI**: the analyzer-neutral semantic interchange specification.
* **Semantic model**: a set of semantic facts and claims expressed using CSMI
  concepts, independently of a particular serialization.
* **CSMI document**: a serialization of one or more semantic models together
  with the metadata required by that serialization.
* **CSMI pack**: a distributable artifact containing semantic documents plus an
  applicability, provenance, and integrity envelope.
* **JSON serialization**: the first normative mapping from the semantic model to
  JSON.
* **JSON Schema**: the structural validator for that JSON serialization.
* **Producer**: a tool that derives and emits semantic information.
* **Consumer**: a tool that reads semantic information and interprets it under
  this specification.
* **Target artifact**: the dependency, package, binary, or source artifact whose
  behavior is being described.
* **Core**: concepts that all conforming producers and consumers of a semantic
  family MUST understand or reject explicitly under the extension rules.
* **Required semantics**: semantics without which a consumer cannot interpret
  the affected model correctly. A consumer that does not support them MUST
  report the model as uninterpretable rather than silently ignore them.
* **Optional semantics**: additional semantics that a consumer MAY ignore
  without changing the meaning or completeness of the remaining model.
* **Profile**: a standard, versioned semantic vocabulary built from CSMI
  extension mechanics.
* **Extension**: a namespaced, versioned vocabulary that is not required for
  basic CSMI interpretation.

### 1.4 Repository documents

`specification.md` is the source of truth for semantic meaning and conformance.
The illustrative material in the repository README and examples is explanatory
and non-normative. For v0.1, the normative set consists of:

1. this specification;
2. `schema.json`;
3. valid and invalid structural fixtures;
4. semantic conformance fixtures.

Pack examples show complete documents rather than isolated fragments, but they
do not override the normative prose, schema, or conformance fixtures.

## 2. Versioning

### 2.1 Semantic-model version

The CSMI semantic-model version identifies the concepts, their meaning, and
consumer obligations. The 0.x series is experimental: a consumer MUST support a
0.x version explicitly and MUST NOT infer compatibility solely from a shared
major or minor version. Any change to semantics or conformance obligations
requires a new declared semantic-model version.

### 2.2 Serialization version

The JSON serialization has its own identity and evolution rule. A change to the
accepted serialized structure requires a new declared serialization version,
even when semantic interpretation is unchanged. Purely editorial changes do not
require a new declared version.

For v0.1, every document MUST identify the semantic-model version. It MUST also
carry enough serialization identity for a validator to select the corresponding
schema. The exact field placement is decided with the pack manifest design.

Supporting a serialization does not imply support for the semantic-model
version it encodes, and supporting a semantic-model version does not imply
support for every serialization of that model. Unsupported versions are an
explicit outcome, not an empty semantic model.

### 2.3 JSON Schema version

The v0.1 JSON serialization MUST use
[JSON Schema Draft 2020-12](https://json-schema.org/draft/2020-12/), identified
by its official meta-schema URI. JSON Schema defines structural validity; the
normative prose and conformance fixtures define invariants that cannot be
expressed structurally.

### 2.4 Profiles and extensions

Profiles and extensions are independently versioned. They MUST NOT redefine or
reinterpret a core field. They MAY add a vocabulary item when the extension
mechanics permit it. A consumer MUST be able to distinguish:

* an optional extension that may be ignored;
* an extension whose absence changes completeness; and
* a required extension without which the affected facts cannot be interpreted.

## 3. Semantic-core sections

The sections below map the v0.1 workstreams. Their content is added after the
corresponding design issues are resolved.

### 3.1 Artifact and package identity

Defines how a model names and selects the artifact it describes, how package
coordinates relate to immutable artifact identity, and how consumers make an
applicability decision.

### 3.2 Symbol identity

Defines an analyzer-neutral reference contract for declarations, callables,
fields, parameters, and related program entities.

### 3.3 Declarations

Defines the optional declaration facts needed to resolve and interpret semantic
summaries without requiring a universal type system or source AST.

### 3.4 Procedure summaries

Defines procedure ports, locations, directional transfers, and the minimum
semantics that two analyzers can implement consistently.

### 3.5 Completeness and uncertainty

Defines fact-family completeness and the difference between absence of evidence
and evidence of absence.

### 3.6 Effects, profiles, and extensions

Defines the optional effect vocabulary and the namespacing, versioning, and
unknown-vocabulary rules.

### 3.7 Manifest, provenance, and canonicalization

Defines the pack envelope, its applicability and provenance claims, integrity
mechanism, and deterministic representation requirements.

## 4. Conformance

Conformance has four independent dimensions:

| Dimension | Question |
| --- | --- |
| Structural validity | Does the document conform to the declared serialization schema? |
| Semantic validity | Do its references and semantic claims satisfy the specification's invariants? |
| Applicability | Does it match the exact artifact and variant under analysis? |
| Interpretability | Does the consumer support all semantics required to interpret it correctly? |

A successful result in one dimension MUST NOT be reported as proof of another.
In particular, structurally valid JSON is not necessarily semantically valid,
applicable, or interpretable.

### 4.1 Structural conformance

A conforming JSON document MUST validate against the normative schema selected
by its version. The schema MUST reject unknown core object fields using JSON
Schema's closed-object facilities.

### 4.2 Semantic conformance

A conforming implementation MUST preserve the meaning defined by this
specification. In particular:

* a missing fact MUST NOT imply that behavior is absent;
* incompleteness MUST remain distinguishable from an explicit negative claim;
* unknown optional extensions MUST NOT silently change core semantics; and
* producers MUST be distinguishable from the artifact whose semantics they
  describe.

### 4.3 Independence requirement

Two independently implemented consumers MUST be able to assign the same meaning
to a core CSMI fact without using producer source code, producer internal
serialization, hidden side channels, or analyzer-specific name parsing.

### 4.4 Inconclusive and unsupported outcomes

A consumer MUST NOT collapse malformed input, semantic invalidity,
inapplicability, an unsupported version, unsupported required semantics, or
incomplete coverage into a model with no facts. Each condition MUST remain
distinguishable from a complete claim that modeled behavior is absent.

## 5. Open design decisions

These decisions MUST be resolved before v0.1 becomes candidate-complete. The
initial draft positions are review proposals, not final normative choices.

| Decision | Initial draft position | Linked issue |
| --- | --- | --- |
| Package coordinate standard | Use Package URL as the primary coordinate and define deterministic applicability rules around it. | #2 |
| Immutable identity | Permit digests; require them only where a package coordinate cannot safely identify the modeled binary or variant. | #2 |
| Symbol representation | Define a structured analyzer-neutral contract rather than requiring consumers to parse language-specific fully qualified names. | #3 |
| Existing symbol schemes | Reuse established concepts where practical, but do not adopt another grammar wholesale without resolving ownership and extensibility. | #3 |
| Declaration scope | Include only resolution-bearing facts required by summaries; keep complete language type systems out of core. | #4 |
| Transfer meaning | Treat a transfer as directional may-flow unless a separately defined relation kind proves necessary. | #5 |
| Completeness scope | Define completeness independently for each fact family rather than as a single pack-wide flag. | #6 |
| Core effects | Keep only broadly portable effect concepts in core; express specialized domains as versioned profiles. | #7 |
| Extension requirement | Make required extensions explicit so consumers can fail closed for affected facts instead of ignoring them. | #7 |
| Canonicalization | Prefer deterministic producer requirements and a defined content address; defer broad canonical JSON policy only if it is unnecessary for integrity. | #8 |
| Distribution | Exclude transport and registry protocols from v0.1. | #8 |
