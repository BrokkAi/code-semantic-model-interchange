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
| Pack | The distributable envelope for semantic documents, assembly, licensing, and integrity metadata. |
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
  assembly, licensing, and integrity envelope.
* **Semantic producer**: a versioned tool or maintained process that establishes
  semantic facts or completeness claims.
* **Pack assembler**: a versioned tool or maintained process that selects and
  packages existing resources without thereby becoming their semantic producer.
* **Pack digest**: the content address computed from the canonical pack manifest.
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
* **Standard profile**: a CSMI-governed, versioned semantic vocabulary built
  from the extension mechanics in section 3.6.
* **Vendor extension**: a publisher-governed, namespaced, versioned semantic
  vocabulary built from the same mechanics.
* **Vocabulary use**: one use of an exact standard-profile or vendor-extension
  version, including whether that use is required or optional and which
  semantic units it affects.

### 1.4 Repository documents

`specification.md` is the source of truth for semantic meaning and conformance.
The illustrative material in the repository README and examples is explanatory
and non-normative. For v0.1, the normative set consists of:

1. this specification;
2. `schema.json`;
3. valid and invalid structural fixtures;
4. semantic conformance fixtures.

Complete representative documents live under `fixtures/valid/`. Files under
`examples/` may group isolated component cases for explanation and do not
override the normative prose, schema, or conformance fixtures.

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

For v0.1, every semantic document MUST identify the semantic-model version and
serialization version and MUST carry enough schema identity for a validator to
select the corresponding schema. A pack resource descriptor repeats only the
media type and byte-level integrity information needed before parsing; it does
not replace the document's self-description.

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

Standard profiles and vendor extensions are independently versioned semantic
vocabularies. They use the same mechanics and differ in namespace authority and
governance, not in whether a consumer must implement them. Neither may redefine
or reinterpret a core field.

Every vocabulary use is either `optional` or `required` for explicitly affected
semantic units. If ignoring a vocabulary would change a core fact, applicability,
binding, completeness claim, or another supported fact, that use is `required`.
There is no third "completeness-changing" category: completeness-changing uses
are required semantics. Section 3.6 defines namespace, version, schema,
attachment, and unsupported-vocabulary behavior.

### 2.5 Normative JSON mapping

The canonical schema identifier for the v0.1 JSON serialization is
`https://csmi.brokk.ai/schema/0.1/schema.json`. The URI identifies the schema;
validation MUST NOT depend on retrieving it over the network. The repository
copy at `spec/0.1/schema.json` is normative.

The schema accepts exactly two root document types, selected by the required
`documentType` discriminator:

- `semantic-document` carries `semanticModelVersion` `0.1`,
  `serializationVersion` `0.1-json`, the canonical `schema` URI, producer
  provenance, and one or more semantic models; and
- `pack-manifest` carries `packFormatVersion` `0.1`, the same canonical `schema`
  URI, assembler and licensing metadata, and resource descriptors under
  section 3.7.

Every semantic model carries its own alternative artifact selectors and any
compatibility constraints. Its `symbols` array defines document-local ASCII
handles for structured symbol keys. A symbol entry without its own
`artifactSelectors` inherits the enclosing model's artifact identity scope. A
symbol entry with `artifactSelectors` names an external artifact scope. The
handle is only a compact reference within that semantic model: it is not CSMI
symbol identity, MUST be unique within the model, and MUST NOT be compared
across models or documents. The full identity remains the artifact scope,
scheme, exact scheme version, stability, and ordered descriptor path from
section 3.2.

References from declarations, relationships, type expressions, summaries,
completeness scopes, and extension envelopes resolve against that same model's
symbol entries. Provenance handles resolve against the enclosing document's
`provenanceRecords`. JSON Schema validates handle syntax but cannot prove that a
handle exists, is unique, has the required category or scope, or denotes the
same semantic identity as another handle. Those are semantic-conformance checks.

The model-level `consumerResolvedDependencies` set declares every declaration
aspect that facts in that semantic model require a consumer to supply under
section 3.3.6. A dependency is shared rather than attached to one fact: each
core fact's rules determine which aspects it requires, and semantic validation
MUST verify that every required aspect is either embedded or present in this
set.

Core facts use family-specific arrays: `declarations`, `relationships`,
`procedureSummaries`, and `completenessStatements`. Namespaced families use
`extensionFacts`. A vocabulary-owned attachment may appear only in an explicit
`extensions` array on a schema-defined core object. Each attachment or
extension fact names the exact vocabulary and version and contains one
vocabulary-owned `payload`; arbitrary new properties on the core object remain
invalid.

The core schema deliberately accepts the contents of vocabulary-owned
`payload`, projection-step `args`, compatibility values, extension-family
scopes, and affected-unit targets as JSON whose detailed shape belongs to the
named vocabulary schema. A consumer that supports that exact vocabulary version
MUST validate those values at their declared attachment points. Passing only the
core schema does not establish profile-payload structural validity or semantic
support, and an unsupported schema URI MUST NOT trigger an automatic network
fetch.

The serialization classifies arrays as follows:

| Array kind | Core arrays |
| --- | --- |
| Ordered sequence | symbol `descriptors`; declaration `genericParameters`; callable `parameters` and `results`; type `arguments`; relationship `typeArguments`; dependency `typeArguments`; projection `steps` |
| Unordered set | semantic models, selectors, digests, provenance records and inputs, compatibility constraints, vocabulary uses and affected units, consumer-resolved dependencies, symbols, declarations, relationships, procedure summaries and transfers, extension facts and attachments, completeness statements and limitations, provenance references, external identities, pack resources, and predecessor digests |

Ordered sequences retain their defined order. Producers canonicalize every
set-valued array under section 3.7.5. An optional set-valued field MUST be
omitted when empty. The schema permits explicit empty arrays only where empty is
semantically distinct or structurally required: callable parameters, callable
results, and a procedure summary's transfer set. No core field accepts `null`
as an alternate encoding for absence.

## 3. Semantic-core sections

The sections below map the v0.1 workstreams. Their content is added after the
corresponding design issues are resolved.

### 3.1 Artifact and package identity

An artifact selector identifies a package or distribution and constrains the
artifacts to which a semantic model applies. Artifact identity is independent
of producer identity: changing the producer does not change the modeled
artifact, and changing the modeled artifact does not change the producer.

#### 3.1.1 Package coordinates

An artifact selector MUST contain one canonical
[Package URL (PURL)](https://ecma-international.org/publications-and-standards/standards/ecma-427/)
conforming to ECMA-427 and to the registered definition of its PURL type. A
producer MUST preserve the type-specific meaning, case rules, normalization,
and qualifiers defined by PURL; it MUST NOT apply CSMI-specific reinterpretation
to individual PURL components.

Package identity comparison MUST compare canonical PURL components rather than
raw input strings. A qualifier present in the selector is a constraint and MUST
have an equivalent value in the candidate artifact. If comparable candidate
evidence has a different value, the selector is not matched; if the candidate
does not expose that qualifier, applicability is indeterminate. Additional
candidate qualifiers do not contradict a selector that intentionally applies
more broadly.

The PURL identifies a package or distribution. It does not by itself prove that
the consumer has the same bytes the producer modeled. Consumers MUST NOT treat
different PURL type, namespace, or name components as aliases without external,
trusted equivalence evidence.

The PURL `subpath` component MUST NOT appear in a v0.1 artifact selector. CSMI
symbol and declaration identity identifies entities within the selected
artifact; using `subpath` for this purpose would create a second, ambiguous
program-entity identity mechanism.

#### 3.1.2 Exact versions and version ranges

A selector MUST use exactly one of these version forms:

- an exact version in the PURL `version` component; or
- a [VERS](https://www.packageurl.org/docs/vers/introduction) constraint whose
  scheme is applicable to the selector's PURL type.

A selector MUST NOT contain both an exact PURL version and a VERS constraint.
Free-form version ranges and non-canonical VERS strings are invalid. The VERS
type MUST equal the selector's PURL type. A producer MUST NOT compare versions
using lexical ordering, Semantic Versioning, or any other substitute for the
comparison procedure selected by VERS.

The VERS type MUST have a registered comparison procedure or a procedure fully
defined by a CSMI vocabulary use declared `required`. A range with no specified
comparison procedure is semantically invalid; merely accepting its URI syntax
is not sufficient.

A consumer that does not implement the applicable VERS scheme MUST return an
indeterminate applicability result. It MUST NOT guess whether the version is in
range.

PURL and VERS apply percent-encoding independently. When deriving a VERS
constraint from a PURL version, a producer MUST decode the PURL component once
and then encode the resulting version under VERS rules. It MUST NOT splice an
encoded PURL component directly into a VERS string.

#### 3.1.3 Artifact digests

A selector MAY contain one or more cryptographic digests of the modeled
artifact. A digest identifies exact content and is separate from the package
coordinate and version constraint.

A digest is REQUIRED when the modeled semantics depend on exact content that
the canonical PURL and version constraint do not identify unambiguously. This
includes at least:

- a locally built, patched, repackaged, or otherwise non-registry artifact;
- an ecosystem coordinate that can select multiple relevant binaries or source
  distributions without identity-bearing qualifiers sufficient to distinguish
  them; and
- semantics derived from build features, generated code, platform variants, or
  classifiers that the PURL type cannot represent completely.

A producer SHOULD include a digest whenever it has the exact artifact bytes,
even when the digest is not required. A producer MUST state what byte sequence
each digest covers, such as an archive, binary, source distribution, or image
manifest. Any coverage kind that requires canonicalization, including a source
tree, MUST identify the canonicalization procedure. A consumer MUST compare
only digests with the same algorithm, coverage kind, and canonicalization
procedure.

The v0.1 core supports the `sha-256`, `sha-384`, and `sha-512` names from the
[IANA Hash Function Textual Names registry](https://www.iana.org/assignments/hash-function-text-names).
Digest values MUST use lowercase hexadecimal with the full output length of the
selected algorithm. SHA-1 MUST NOT be produced. Additional algorithms require a
profile or extension until the core set is expanded.

Digest coverage kinds within a selector are conjunctive. Multiple algorithms
for the same coverage kind are alternative ways to establish that content: at
least one comparable digest MUST match and every comparable digest MUST agree.
Any comparable mismatch makes that selector not matched. If the consumer cannot
compute any listed algorithm for a required coverage kind, or lacks the covered
bytes, applicability is indeterminate.

#### 3.1.4 Alternatives and constraint composition

A semantic model MAY declare multiple artifact selectors. Selectors are
alternatives: the model is applicable if any selector matches. Within one
selector, the package coordinate, version constraint, PURL qualifiers, and all
required digest evidence are conjunctive and MUST all be satisfied.

Producers SHOULD use multiple selectors only when the same semantic claims and
completeness claims apply to every alternative. If behavior or completeness
differs by artifact version or variant, the producer MUST use separate semantic
models or separately scoped claims rather than a broader selector.

#### 3.1.5 Applicability outcomes

Matching one selector produces exactly one of these outcomes:

**matched**
: Every required constraint has comparable evidence and is satisfied.

**not matched**
: At least one required constraint has comparable evidence and is contradicted.

**indeterminate**
: No required constraint is contradicted, but evidence or comparison support
  needed to establish a match is unavailable.

For multiple alternative selectors, a single `matched` result makes the model
applicable. Otherwise, the combined result is `indeterminate` if any selector is
indeterminate, and `not matched` only if every selector is not matched.

An indeterminate result MUST NOT be treated as matched or not matched. A default
consumer MUST fail closed and decline to apply the model. A consumer MAY expose
an explicit trust policy that permits an operator to override this behavior,
but the reported applicability result remains indeterminate and the override
MUST be observable.

#### 3.1.6 Matching procedure

For each selector, a consumer MUST:

1. parse and validate the PURL under ECMA-427 and its registered type;
2. reject a selector containing `subpath`, both version forms, or neither an
   exact version nor a VERS constraint;
3. compare canonical package identity and selector qualifiers using the PURL
   type's equivalence rules;
4. compare the exact version or evaluate VERS using the applicable ecosystem
   procedure;
5. compare every required artifact digest for which comparable bytes and an
   algorithm implementation are available; and
6. combine the evidence using the outcomes in section 3.1.5.

A malformed selector is semantically invalid, not indeterminate. A valid
selector with insufficient evidence is indeterminate.

#### 3.1.7 Compatibility constraints

Runtime, toolchain, ABI, language edition, operating system, and hardware
constraints that select a distinct package artifact SHOULD use identity-bearing
qualifiers defined by the applicable PURL type. Compatibility constraints that
describe where already-selected artifact semantics hold, rather than which
artifact is selected, are a separate CSMI concept and MUST NOT be encoded as
invented PURL qualifiers.

Compatibility constraints MUST be declared separately from artifact selectors
and evaluated only after artifact applicability. A profile defining a
compatibility constraint MUST define its namespace, version, value syntax,
comparison procedure, and composition rules. CSMI 0.1 does not define a
universal toolchain or runtime version scheme.

Compatibility evaluation produces `compatible`, `incompatible`, or
`indeterminate`. A consumer that cannot interpret a required compatibility
profile MUST report the model as uninterpretable. A consumer that understands
the profile but lacks comparison evidence MUST report compatibility as
indeterminate. Both outcomes fail closed by default and neither changes the
artifact applicability result.

### 3.2 Symbol identity

CSMI symbol identity names a program entity within one modeled artifact without
requiring a consumer to parse a producer's fully qualified name. A symbol key is
the tuple of:

1. the enclosing model's artifact identity scope;
2. a versioned identity scheme;
3. an ordered descriptor path constructed under that scheme; and
4. an identity stability class.

The artifact identity scope contains the alternative selectors defined in
section 3.1 and supplies package and version identity. A symbol key MUST NOT
repeat a package manager, package name, package version, or artifact digest. Two
otherwise identical symbol keys in different artifact identity scopes are
different symbols unless a separately declared relationship establishes
equivalence.

One symbol key MAY apply across every alternative selector in its artifact
scope only when the identity scheme constructs the same descriptor path for the
entity in every alternative. If identity differs between alternatives, the
producer MUST narrow the artifact scope or declare separate symbols.

#### 3.2.1 Identity schemes

Every symbol key MUST name an identity scheme and its version. An identity
scheme defines:

- which source language or binary interface it identifies;
- how descriptor paths are constructed from language entities;
- normalization and comparison rules for descriptor names;
- how overloads and otherwise colliding declarations are disambiguated;
- how constructors, operators, extension members, generated declarations,
  generic entities, and unnamed entities are represented; and
- whether artifact-local identities are supported and stable.

Scheme identifiers MUST be globally unambiguous. Standard profiles use names
assigned by CSMI; non-standard schemes use the namespaced extension mechanism
defined for CSMI profiles and extensions. A scheme version identifies its
identity and comparison rules, not the version of the producer that emitted the
key.

An identity scheme MUST be deterministic: two conforming producers observing
the same entity in the same artifact MUST construct equivalent symbol keys.
Producer-assigned database IDs, traversal order, source offsets, hashes of
display strings, and analyzer-internal fully qualified names MUST NOT be used by
a portable identity scheme unless the scheme normatively defines their stable
construction and equivalence.

A consumer that does not support a symbol's required identity scheme MUST
report the affected model as uninterpretable. It MUST NOT compare unsupported
scheme payloads as opaque strings and infer identity from equality alone.

CSMI 0.1 does not define a single universal language identity scheme. Language
or ABI identity schemes are versioned profiles. This preserves an
analyzer-neutral envelope while allowing Java, Python, JavaScript/TypeScript,
Rust, and other ecosystems to use their actual binding and overload semantics.

#### 3.2.2 Descriptor paths

A descriptor path is an ordered, non-empty sequence from the artifact-visible
root to the identified entity. Each descriptor contains:

- a `role` from the portable role vocabulary;
- a scheme-normalized `name`, when the entity is named; and
- a scheme-defined `disambiguator`, when the role and name do not uniquely
  identify the entity among siblings.

The portable roles are:

| Role | Meaning |
| --- | --- |
| `namespace` | A namespace, module, package, crate, or comparable naming container. |
| `type` | A class, interface, trait, enum, type alias, or comparable type-level entity. |
| `term` | A value, field, constant, property, or non-callable member. |
| `callable` | A function, method, constructor, accessor, operator, or comparable invocation target. |
| `type-parameter` | A type, const, value, lifetime, or comparable generic parameter owned by the preceding entity. |
| `value-parameter` | A receiver, positional, named, variadic, or comparable callable parameter. |
| `meta` | A macro, annotation member, compiler metadata entity, or other scheme-defined meta-level entity. |

Roles describe path structure, not the complete declaration kind. For example,
a Java class and Rust struct both use `type`; their precise kinds belong to the
portable declaration model. Consumers MUST NOT infer language-specific kind or
behavior solely from a descriptor role.

Names are individual path components, not a delimited FQN. A producer MUST NOT
place `java.util.List`, `crate::module::Type`, or another compound path into one
descriptor merely to avoid constructing the enclosing descriptors.

#### 3.2.3 Overloads and callable identity

A callable descriptor MUST include a disambiguator whenever two callable
entities with the same normalized name and owner can coexist. The identity
scheme MUST define the disambiguator from resolver-visible declaration
semantics, such as a canonical callable signature, ABI symbol, or other stable
language identity.

An overload ordinal such as `+1`, source declaration order, or a hash with no
normative preimage and algorithm MUST NOT be the sole portable disambiguator.
Return types, generic arity, receiver kind, parameter labels, parameter types,
calling convention, and other signature elements participate only where the
identity scheme says they distinguish declarations in that language.

Constructors, destructors, getters, setters, operators, and extension members
use the `callable` role. The scheme MUST define their normalized names and the
semantic owner used in the descriptor path. For an extension member, the
declaration container and extended receiver type MUST NOT be conflated; the
scheme must identify which one establishes symbol ownership and how the other
participates in disambiguation or declarations.

#### 3.2.4 Generics and instantiated types

A descriptor path identifies a declared generic entity, its declared generic
parameters, and callable value parameters. A use-site instantiation such
as `List<String>` or `Vec<u8>` is a type expression, not a new declaration, and
MUST NOT be represented as a new symbol key unless the identity scheme defines
an independently declared specialization as a distinct entity.

Type and value parameter identity is owner-relative. A scheme SHOULD use a
declared name when that name participates in language identity; otherwise it
MUST define a stable owner-relative position or role. Display names alone MUST
NOT determine parameter identity.

#### 3.2.5 Stability classes

Every symbol key declares one of these stability classes:

**portable**
: The identity scheme guarantees deterministic construction for independently
  implemented producers without requiring exact-content digest scope. The
  entity's source-language visibility does not affect this classification.

**artifact-local**
: The entity has no stable externally visible identity, but the identity scheme
  guarantees deterministic construction within one exact artifact.

An artifact-local symbol MUST be scoped so that every alternative artifact
selector has required exact-content digest evidence. Its scheme MUST define the
artifact-internal root, local ownership chain, and deterministic local
disambiguator. Source line or byte offsets MAY appear as diagnostic provenance
but MUST NOT be the sole identity because formatting or generated-source
presentation may change without changing the compiled entity.

If no supported scheme can construct a deterministic artifact-local identity,
the entity cannot be a CSMI semantic target. A producer MUST report the omission
with a `partial` `declaration-records` statement and an
`unsupported-semantics` limitation, or leave coverage `unknown`; it MUST NOT
mint an unstable ID or claim complete declaration-record coverage.

#### 3.2.6 Display and external identities

A symbol declaration MAY carry a human-readable display name, qualified display
name, language-native signature, documentation name, ABI name, or identities
from external schemes such as SCIP. These values are aliases or presentation
metadata and are not part of the CSMI symbol key unless the declared identity
scheme explicitly adopts them.

A declaration MAY also classify its origin as `named`, `generated`, `synthetic`,
or `local`. Origin records how the entity arose; it does not by itself determine
identity or stability. A generated entity can have a portable identity, and a
named local entity may require artifact-local identity. Consumers MUST use the
identity scheme and stability class rather than origin metadata when comparing
symbols.

Each external identity MUST name its scheme and version. A consumer MUST NOT
infer equivalence between a CSMI symbol and an external identity merely because
their display text is equal. An asserted external identity is a producer claim;
a consumer MAY verify it using the external scheme before using it for lookup.

#### 3.2.7 Comparison and resolution

Symbol comparison produces one of these outcomes:

**same**
: Artifact scope, identity scheme and version, stability class, and every
  descriptor compare equal under the scheme.

**different**
: The consumer supports the scheme and at least one comparable identity
  component differs.

**indeterminate**
: No component is contradicted, but the consumer lacks the scheme support or
  artifact evidence needed to establish equality.

Unsupported identity schemes make the affected model uninterpretable for
semantic application even if a consumer can preserve or display their encoded
form. A consumer MUST NOT fall back to display names, source text, simple-name
matching, or analyzer-specific FQN parsing to turn an indeterminate result into
`same` or `different`.

#### 3.2.8 Relationship to SCIP

[SCIP](https://github.com/scip-code/scip) is important prior art. CSMI reuses
its central insight that identity is an ordered descriptor path with explicit
descriptor roles and overload disambiguation. CSMI does not embed the SCIP
symbol string as its core identity because SCIP combines its own package tuple
with descriptors, permits document-local IDs, and leaves construction details
to language indexers.

A SCIP mapping profile MAY map a supported SCIP scheme and descriptor path into
a CSMI identity scheme. The mapping MUST bind SCIP package information to the
CSMI artifact selector, define overload-disambiguator equivalence, and reject
SCIP local symbols unless it can satisfy the artifact-local requirements in
section 3.2.5.

#### 3.2.9 Relationship to SemanticDB, Kythe, and LSIF

[SemanticDB](https://scalameta.org/docs/semanticdb/specification.html) likewise
uses owner-relative symbol descriptors and compiler-resolved occurrences. Its
global and local symbol distinction supports CSMI's separation between portable
and artifact-local identity, but its language/compiler-specific symbol grammar
is not adopted as a universal CSMI key.

[Kythe](https://kythe.io/docs/schema/) uses structured VNames containing corpus,
root, path, language, and signature. This demonstrates the value of separating
identity dimensions and discouraging source locations for semantic nodes.
However, Kythe permits indexers to choose signatures whose stability need not
extend across input versions, so a raw VName is an external identity rather
than sufficient proof of CSMI portability.

[LSIF](https://microsoft.github.io/language-server-protocol/specifications/lsif/0.4.0/specification/)
monikers associate scheme-specific identifiers with package information for
cross-project navigation. A mapping profile may preserve such monikers as
external identities, but CSMI artifact scope remains authoritative and the
moniker scheme must define deterministic symbol equivalence before it can serve
as a CSMI identity scheme.

### 3.3 Declarations

The declaration model supplies only the resolution-bearing facts needed to bind
and interpret CSMI semantic facts. It is a flat graph keyed by the symbol keys
defined in section 3.2. It is not a source AST, a replacement compiler model, or
a universal type system.

A declaration model contains declaration records and directional relationship
records. A declaration record MUST identify exactly one symbol and one portable
declaration category. It MAY add an owner, generic parameters, a callable
shape, an alias target, and presentation metadata where those facts are
applicable. A producer MUST NOT encode source declarations as nested syntax
merely to preserve their original textual form.

#### 3.3.1 Portable declaration categories

The core declaration categories are:

| Category | Core meaning |
| --- | --- |
| `namespace` | A package, module, namespace, crate, or comparable naming container. |
| `type` | A named type-level declaration, including a class, interface, trait, protocol, struct, enum, or comparable entity. |
| `type-alias` | A declared name whose target is another type expression under language-defined alias rules. |
| `value` | A field, property, constant, variable, enum case, or comparable non-callable value. |
| `callable` | A function, method, constructor, accessor, operator, destructor, or comparable invocation target. |
| `type-parameter` | A generic type, const, value, or lifetime parameter owned by another declaration. |
| `value-parameter` | An explicit callable parameter. |
| `meta` | A macro, annotation member, compiler metadata entity, or other scheme-defined meta-level declaration. |

The declaration category MUST agree with the terminal descriptor role under the
symbol's identity scheme. `type` and `type-alias` both use a `type` descriptor;
the remaining categories use their same-named descriptor role, except `value`,
which uses `term`.

Categories are deliberately coarser than language declaration kinds. A Java
class, TypeScript interface, and Rust trait are all `type` declarations. Their
language-native kind MAY be presentation metadata or a profile fact, but a
consumer MUST NOT infer portable behavior from that metadata. Relationships
and callable shapes carry the core distinctions that affect resolution.

#### 3.3.2 Ownership and members

An `owner` is a symbol reference naming the declaration that lexically or
semantically contains another declaration under the identity scheme. Ownership
is directional from the owned declaration to its owner. A producer MUST encode
membership once through `owner`; it MUST NOT also create a second nested member
identity.

An owner MUST have the same artifact identity scope as the owned declaration.
It MUST be compatible with the owned declaration's descriptor path and identity
scheme. A namespace or top-level declaration MAY have no declared owner. A
value parameter MUST be owned by its callable, and a type parameter MUST be
owned by the generic declaration that introduces it.

Omission of an owner is not evidence that a declaration is top-level. A
consumer may make that inference only when the identity scheme itself proves it
or when declaration completeness covers ownership for that symbol.

#### 3.3.3 Callable shapes

A callable declaration MAY contain one callable shape. When present, the shape
is an atomic and complete account of invocation binding at the modeled semantic
level; it contains:

- a callable kind;
- zero or one receiver;
- every explicit value parameter in declaration order; and
- every logical result in result order.

This is structural completeness for that callable shape: it does not assert
that the producer's declarations, types, relationships, or behavioral facts are
otherwise complete. Individual receiver, parameter, and result types may be
omitted or `unknown` without making the invocation-slot sequence partial.

The core callable kinds are `function`, `method`, `constructor`, `accessor`,
`operator`, `destructor`, and `other`. Callable kind does not determine
identity, dispatch, allocation, effects, or result behavior unless another core
rule or semantics from a vocabulary use declared `required` says so.

A receiver has one of these kinds:

| Receiver kind | Meaning |
| --- | --- |
| `instance` | Invocation supplies an instance value as the receiver. |
| `type` | Invocation supplies a type or class value as the receiver. |
| `extension` | Invocation syntax treats a value as the receiver although the declaration owner is different. |

Absence of a receiver means that invocation does not supply one. This includes
module-level functions, static or associated callables, and constructors at
entry. A consumer MUST NOT infer receiver presence from the owner or callable
kind. An extension receiver MUST NOT be conflated with the declaration owner.
The receiver MAY carry a minimal type expression.

Each explicit parameter has a zero-based `position` and one binding form:

| Binding form | Meaning |
| --- | --- |
| `positional-only` | Bound only by its invocation position. |
| `positional-or-named` | Bound by position or a resolver-significant label. |
| `named-only` | Bound only by a resolver-significant label. |
| `variadic-positional` | Collects zero or more remaining positional arguments. |
| `variadic-named` | Collects zero or more remaining named arguments. |

Positions MUST be unique, contiguous, and ordered from zero. The receiver and
generic parameters are not members of this sequence. A resolver-significant
`label` is REQUIRED for `positional-or-named` and `named-only` parameters and
OPTIONAL otherwise. A label on a positional-only or variadic collector is
presentation metadata unless a vocabulary use declared `required` gives it
resolver semantics.
Every parameter MUST have a `required` flag recording whether invocation may
omit it; a default value expression is outside the v0.1 core. A parameter MAY
reference its `value-parameter` symbol and MAY carry a minimal type expression.

Each logical result has a unique, contiguous, zero-based position and MAY carry
a label and type expression. An empty result sequence represents no logical
result under the applicable language or ABI profile. Constructors do not gain
an input receiver merely because invocation may produce a constructed value;
the applicable profile defines how that value appears among logical results.

#### 3.3.4 Generic parameters and minimal type expressions

A generic declaration MAY contain an ordered list of generic parameters. Each
entry MUST reference a `type-parameter` symbol owned by that declaration, have a
unique contiguous zero-based position, and classify the parameter as `type`,
`value`, or `lifetime`. Bounds, variance, defaults, higher-kinded parameters,
and language-specific constraint systems are outside the core unless required
by a profile.

When a generic-parameter list is present, it MUST enumerate every generic
parameter introduced by that declaration in declaration order. Omitted or
profile-owned bounds do not make that parameter sequence structurally partial.

The v0.1 core type-expression vocabulary contains only:

**reference**
: A symbol reference to a declared type or type alias, optionally
  followed by an ordered list of type arguments.

**parameter**
: A reference to a generic parameter symbol.

**intrinsic**
: A type atom defined by a namespaced, versioned profile use declared
  `required`, such as a
  language primitive that has no declaration symbol in an artifact.

**unknown**
: A type position exists, but the producer cannot express a type for it in the
  supported vocabulary.

A reference MAY name a symbol in another artifact identity scope. In that case,
the target artifact scope is part of the symbol reference. A consumer must have
the artifact identity evidence and scheme support needed to compare that symbol
reference, but need not establish that a separate semantic model for the target
artifact is applicable merely to use the type identity. If semantic facts about
the external artifact are applied, their own artifact applicability is still
required. An intrinsic type MUST name its profile, profile version, and
profile-defined identifier; a consumer that does not support the profile use
declared `required` cannot interpret the affected type fact. Arrays, tuples,
function types, unions, intersections, nullability, mutability, ownership,
lifetimes, wildcards, variance, and structural types require profiles unless
represented as declared symbols or profile-defined intrinsics.

Two type references are equal in core only when their symbol identities compare
`same` and their type arguments recursively compare equal in order. Intrinsics
compare only under their named profile and version. `unknown` does not compare
equal to another type merely because both are unknown. A consumer MUST NOT
infer cross-language primitive equivalence, expand aliases, erase generic
arguments, or apply a language subtype relation unless required semantics
define that operation.

A `type-alias` declaration MUST have one alias target expressed with this
vocabulary or a vocabulary use declared `required`. The alias remains a
distinct declaration; its presence does not make the alias symbol and target
symbol identical.

#### 3.3.5 Declaration relationships

A relationship is directional from a subject symbol through a predicate to an
object. For `inherits` and `conforms-to`, the object is a referenced type symbol
and MAY carry ordered type arguments. For `overrides` and `implements`, the
object is a member symbol. The core predicates are:

| Predicate | Subject to object meaning |
| --- | --- |
| `inherits` | A type directly declares the object type as a base from which implementation or members may be inherited. |
| `conforms-to` | A type directly declares conformance to the object interface, trait, protocol, or comparable contract. |
| `overrides` | A callable or value is declared by the source language or ABI to directly override the object member. |
| `implements` | A callable or value directly realizes the resolved object contract member. |

Core relationships record resolver-proven declarations, not name similarity or
inferred transitive closure. They do not by themselves define structural
subtyping, method resolution order, dispatch targets, variance, layout, or
binary compatibility. A producer MUST declare a corresponding vocabulary use
`required` when those language-specific consequences are necessary to
interpret a semantic fact.

Relationship objects and type expressions MAY refer across artifact scopes.
Ownership MUST NOT. A consumer lacking comparable identity evidence for an
external endpoint cannot use the affected relationship to establish resolution.

#### 3.3.6 Optional and consumer-resolved declarations

Declarations are an optional fact family. A producer MAY omit declaration facts
that no other emitted semantic fact needs. Absence remains unknown unless an
applicable `declaration-aspects` completeness claim proves the declaration fact
is absent.

Every semantic fact that needs declaration information MUST either:

1. include the required declaration aspect in the same applicable pack; or
2. explicitly declare a consumer-resolved dependency naming the symbol,
   declaration aspect, and any predicate or endpoint required to identify the
   fact.

The core declaration aspects are `category`, `owner`, `generic-parameters`,
`callable-shape`, `alias-target`, and `relationships`. A dependency on a
single-valued aspect requests its complete value. A relationship dependency
MUST identify the required predicate, object, and type arguments, if any. A
requirement for a complete relationship set additionally needs an applicable
`declaration-relationships` completeness claim under section 3.5; absence of an
unlisted relationship is not enough. A reference to a declaration-defined
aspect with neither embedded facts nor an explicit consumer-resolved dependency
is semantically invalid.

A consumer MAY satisfy a consumer-resolved dependency from its own declaration
index only after establishing artifact applicability and symbol-scheme support.
It MUST map the local evidence through a supported identity scheme and every
applicable vocabulary use declared `required` into the requested CSMI
declaration aspect, then compare that aspect using this section's structural
and semantic rules. Display-name
equality, analyzer FQN parsing, source-text similarity, or producer-specific IDs
MUST NOT establish equivalence. The consumer MUST preserve the local fact's
provenance and report that interpretation was supplemented. Local facts MUST
NOT repair an unsupported symbol scheme or silently turn a self-contained pack
claim from incomplete into complete.

If a required consumer-resolved fact is unavailable, the local evidence's
artifact applicability is indeterminate, or its semantics are unsupported, the
affected model is uninterpretable. A default consumer MUST fail closed. This
option permits a consumer that already has equivalent compiler or analyzer
declarations to avoid redundant pack data without making that dependency
invisible.

#### 3.3.7 Duplicate and conflicting facts

Within one semantic model, a symbol MUST have at most one declaration record.
Repeated facts from multiple applicable models or sources are equivalent only
when their artifact scopes and symbol identities compare `same` and every
asserted core value agrees. Exact duplicate relationships, including equivalent
type arguments, are harmless. Different relationship objects for a multi-valued
predicate are not inherently conflicting.

Omission is not a conflict. A source that lacks an owner, type, relationship, or
other fact does not contradict a source that asserts it unless an applicable
complete claim covers that fact under section 3.5.

An omitted or `unknown` type does not conflict with a known type supplied by
another source; the known type may refine it. Two known type expressions
conflict when they do not compare equal under section 3.3.4 and both sources
assert the same single-valued type position.

Two embedded assertions that assign different values to the same single-valued
aspect are semantically invalid. A conflict between an otherwise valid pack
assertion and consumer-resolved local evidence makes the affected model
uninterpretable. A consumer MUST report the conflict and MUST NOT select a
winner by source priority, input order, producer name, or apparent precision.
Presentation metadata such as display names does not create a semantic conflict.

#### 3.3.8 Relationship to existing declaration models

[SCIP](https://github.com/scip-code/scip/blob/main/scip.proto) separates symbol
identity from fine-grained symbol kind, but its relationships are primarily
navigation metadata and its rendered signature is not a machine-interpretable
callable contract. CSMI therefore uses a smaller portable category vocabulary
and an explicit callable shape.

[SemanticDB](https://scalameta.org/docs/semanticdb/specification.html)
demonstrates useful class, method, type, and value signatures, but its type
model intentionally forms a superset centered on Scala semantics. CSMI adopts
ordered parameters and owner-relative generic declarations without adopting
that complete type algebra.

[Kythe](https://kythe.io/docs/schema/) demonstrates the value of a fact-oriented
graph with typed relationship edges. CSMI uses the same broad graph principle
while defining only the edge semantics required for semantic-model resolution
and leaving language-specific type and dispatch graphs to profiles.

### 3.4 Procedure summaries

A procedure summary describes conservative information transfer across one
invocation of a callable. It relates locations in the invocation's pre-state to
locations in its post-state without exposing the producer's control-flow graph,
data-flow lattice, points-to graph, or heap node identities.

The v0.1 core defines one relation: directional may-information transfer. It
does not define separate value, taint, alias, must-flow, or guarded relation
kinds. Stronger or domain-specific meanings require a versioned profile.

#### 3.4.1 Summary target and declaration dependency

Every procedure summary MUST identify exactly one callable by a symbol key from
section 3.2. The symbol MUST resolve to a `callable` declaration under section
3.3. A summary requires the callable's complete `callable-shape` aspect, either
embedded in the same applicable pack or named as a consumer-resolved dependency
under section 3.3.6.

The callable shape establishes whether a receiver exists and the valid
parameter and logical-result positions. A summary MUST NOT add a receiver,
parameter, or result slot that is absent from that shape. A summary applies to
the exact callable symbol only; it does not automatically apply to overrides,
implementations, aliases, or callables with the same display name.

#### 3.4.2 Boundary roots

A boundary root identifies an invocation-visible value or state before or after
the call. Each root has an explicit `phase`, so the receiver before invocation
is distinct from the receiver state after invocation.

| Phase | Role | Selector and meaning |
| --- | --- | --- |
| `input` | `receiver` | The unindexed receiver supplied to a callable whose declaration has a receiver. |
| `input` | `parameter` | The argument collection bound to one declared zero-based parameter position. |
| `input` | `capture` | A captured value or storage location named by a `value` symbol. |
| `output` | `receiver` | The unindexed receiver-visible state after invocation. |
| `output` | `parameter` | Caller-visible post-state rooted at one declared parameter position. |
| `output` | `capture` | Post-state of captured storage named by a `value` symbol. |
| `output` | `result` | One normal logical result at its declared zero-based result position. |
| `output` | `exception` | The value crossing the immediate exceptional invocation boundary. |

A receiver root is valid only when the callable shape declares a receiver. A
receiver root has no position selector and is separate from the explicit
parameter sequence; a consumer MUST NOT encode it as `receiver[0]` or
`parameter[0]`. A parameter or result root MUST use a position present in the
callable shape. A capture root MUST name a stable symbol in the same artifact
identity scope; the summary's use of that root asserts that the callable
captures the named value or storage. An input `result` or `exception`, or an
output role not listed above, is invalid because core defines result and
exception values only at the post-invocation boundary.

A parameter position is the canonical declaration position from section 3.3.3
for every binding form, including `positional-or-named`, `named-only`, and both
variadic forms. It is not the ordinal at which an argument happens to appear in
call-site source text. A consumer resolves argument labels under the callable
shape first and then binds each argument to its declared `parameter[n]` root.

An output receiver, parameter, or capture denotes externally observable
post-state, not reassignment of the callee's local variable. An unprojected
output parameter is valid only when a language or ABI vocabulary use declared
`required` defines caller-visible writeback, such as an `out` or by-reference
parameter. A
projected output may instead denote mutated state reachable from an ordinary
argument under its projection scheme.

#### 3.4.3 Abstract locations and projection schemes

A boundary location consists of one boundary root followed by zero or more
ordered projections. An empty projection path selects the boundary value or
state as a whole and needs no projection scheme.

A non-empty path MUST name a versioned projection scheme and encode every step
as structured data under that scheme. The scheme MUST define:

- the denotation and canonical representation of each projection kind;
- which roots and preceding projections accept each kind;
- how nested projections compose;
- equality, overlap, and subsumption of projected locations;
- whether a projection selects one concrete location or an abstract set; and
- how a consumer maps the projection to its own memory abstraction.

Projection scheme identifiers use the namespacing and versioning mechanism for
profiles and extensions defined by section 3.6.

Projection schemes may define concepts such as a resolver-proven field, object
attribute, collection elements, map keys or values, tuple components, or future
completion values. A scheme MUST NOT use producer database IDs, traversal
order, source offsets, display names, or opaque analyzer heap-node IDs as
portable projection identity unless it normatively defines their deterministic
construction and equivalence.

A consumer that does not support a required projection scheme or cannot map a
step to the applicable artifact MUST report the affected summary as
uninterpretable. It MUST NOT discard the path, compare its payload as an opaque
string, or replace it with the unprojected root. This permits nested abstract
heap locations without standardizing one analyzer's heap model in core.

#### 3.4.4 Core transfer semantics

A core transfer is an ordered pair of one input-phase source location and one
output-phase destination location. Its implicit relation kind is
`may-information`.

The transfer requires a consumer to conservatively admit that information
associated with the source before invocation may influence or be represented in
the destination after invocation. This includes copying, selection,
aggregation, encoding, calculation, or another derived transformation. A
producer may include an edge as a conservative over-approximation; the edge
does not assert that every invocation or any particular concrete execution
exhibits the flow.

A core transfer does **not** by itself assert:

- object identity, reference equality, or aliasing;
- exact value preservation or invertibility;
- that the source or destination is mutated;
- that the flow occurs on every execution path;
- that no sanitization, validation, encoding, or loss of information occurs;
- a call, callback, allocation, escape, or other effect; or
- the absence of additional transfers.

Core transfers have no guard or path condition. If a transfer is possible only
under some input or control-flow condition, the unguarded may-transfer remains
valid. Must-flow, value-preserving flow, taint propagation, conditional flow,
probabilistic flow, and domain-specific transformations require profiles and
MUST NOT be inferred from a core edge.

The transfer collection is an unordered set. Exact duplicates have no
additional meaning. Because every edge goes from the pre-state partition to the
post-state partition, a procedure summary does not contain internal cycles or
an implicit transitive closure. Interprocedural propagation arises when a
consumer maps one invocation's post-state into later program state and applies
other resolved summaries.

#### 3.4.5 Applying summaries at call sites

To apply a procedure summary, a consumer MUST:

1. establish artifact applicability and exact callable symbol identity;
2. obtain and validate the callable shape required by section 3.4.1;
3. support every projection scheme and vocabulary use declared `required` by
   the summary;
4. bind the resolved call's receiver, arguments, captures, normal results, and
   exceptional continuation to the corresponding boundary roots; and
5. add the summary's may-information transfers to its analysis under the
   reported model provenance and completeness state.

Parameter binding follows the callable shape rather than source-text order or
display names. This includes named arguments: `parameter[n]` remains the same
declared slot regardless of the order in which a call spells its labels. A
variadic parameter remains one declared parameter root; a projection scheme may
select individual or aggregate collected elements. A consumer MUST NOT invent
additional parameter positions for individual variadic arguments.

When dispatch has multiple possible callable targets, a consumer may combine
the applicable transfer sets conservatively, but it MUST preserve unsupported,
inapplicable, and incomplete alternatives. An override or implementation
relationship does not authorize copying a base summary to another callable
unless a vocabulary use declared `required` defines and justifies that
inheritance rule.

A missing or uninterpretable summary does not create a core transfer default.
A consumer MAY use an explicit, named local policy for unknown or external
calls, but that supplementation MUST be observable and MUST NOT change the
reported CSMI transfer set or completeness. In particular, consumers MUST NOT
silently assume universal all-arguments-to-all-outputs flow.

#### 3.4.6 Language and outcome boundaries

Multiple logical results use the positions declared by the callable shape. A
language-level tuple, record, `Result`, or other wrapper remains one logical
result when the callable shape declares one; selecting its components requires
a projection scheme. A consumer MUST NOT reinterpret a wrapper as multiple
result positions from its source spelling alone.

The `exception` root denotes an immediate thrown or raised value that exits the
modeled invocation exceptionally. A normal error value such as Rust `Err`, a
rejected JavaScript promise returned normally, or a language-specific status
code is not an exceptional root unless a vocabulary use declared `required`
defines different invocation semantics.

For an asynchronous callable, the normal result is the returned promise,
future, task, or comparable wrapper. Fulfillment values, rejections, and later
callback arguments require projection or effect profiles that define their
temporal and language semantics. Core transfer edges do not imply that a
callback is invoked.

Constructors have no input receiver under section 3.3.3. A constructor summary
therefore starts from its explicit parameters and captures; the applicable
language or ABI profile determines which logical result or post-state location
represents the constructed value.

#### 3.4.7 Absence, incompleteness, and unsupported semantics

The presence of a procedure summary does not by itself claim that its transfer
set is exhaustive. Only a `complete` claim for the `procedure-summaries` fact
family, applicable to the same callable symbol under section 3.5, closes that
transfer set. Until such a claim applies, an omitted edge remains unknown rather
than false. A complete empty transfer set asserts that the callable has no core
may-information transfers; it does not assert purity or the absence of effects.

A malformed boundary root, a slot inconsistent with the callable shape, an
invalid projection under its scheme, or a transfer whose source is not input
phase or destination is not output phase is semantically invalid. Missing
required declaration evidence or an unsupported required projection or
relation profile makes the affected summary uninterpretable rather than empty.

#### 3.4.8 Prior art and explicit non-goals

[CodeQL model packs](https://codeql.github.com/docs/codeql-language-guides/customizing-library-models-for-java-and-kotlin/)
demonstrate the utility of input-to-output summary edges and rooted access
paths. CSMI adopts those broad ideas but not CodeQL's textual access-path
grammar, language-specific signature matching, generic erasure rules, or
analysis-domain `value` and `taint` kinds.

[IFDS](https://doi.org/10.1145/199448.199462) and implementations such as
[Heros](https://github.com/soot-oss/heros) demonstrate compositional
interprocedural flow functions. Their control-flow nodes, call-to-return edges,
and analysis-specific data facts belong to an analyzer execution model, not the
CSMI boundary contract.

The v0.1 core intentionally does not define:

- source-level or intermediate-representation control-flow graphs;
- points-to sets, alias relations, object identities, or a universal heap;
- must-flow, path conditions, value lattices, or analysis confidence;
- call, callback, allocation, mutation, escape, I/O, or concurrency effects;
- taint sources, sinks, sanitizers, barriers, or threat-model labels;
- exception taxonomies, async state machines, or callback scheduling; or
- a fallback policy for unresolved, external, or unmodeled calls.

### 3.5 Completeness and uncertainty

Completeness describes the coverage of one fact family within one exact semantic
scope. It determines whether omission is merely absence of evidence or may be
interpreted as evidence of absence. It is independent of structural validity,
semantic validity, artifact applicability, interpretability, provenance,
precision, and producer trust.

A completeness statement is a producer assertion. It does not certify that the
producer is correct or that a consuming analysis is sound. Conforming producers
and consumers nevertheless MUST preserve and apply its meaning exactly. This
specification uses *completeness statement* and *completeness claim*
synonymously.

#### 3.5.1 Fact families and coverage scopes

Every completeness statement MUST identify:

1. one fact family;
2. one family-defined coverage scope within the enclosing artifact identity;
3. one coverage status from section 3.5.2; and
4. any limitations required by section 3.5.4 for that status.

Within one semantic model, there MUST be at most one completeness statement for
the same fact family and equivalent coverage scope. Repeating an equivalent
statement or assigning multiple statuses to one scope is semantically invalid.

A fact family defines the semantic universe to which completeness applies. Its
specification MUST define:

- which facts are members of the family;
- the structure and comparison of valid coverage scopes;
- fact equality, conflict, and any semantic subsumption used for coverage;
- whether and how a broader scope covers a narrower scope; and
- the exact closed-world inference licensed by `complete`.

The v0.1 core fact families and scopes defined so far are:

| Family | Coverage scope | Closed set |
| --- | --- | --- |
| `declaration-records` | The target artifact plus one supported identity scheme and version | Every declaration in the artifact governed by that scheme; an entity the scheme cannot identify prevents complete coverage. |
| `declaration-aspects` | One exact symbol and one non-relationship aspect from section 3.3.6 | The complete value, sequence, or absence of that aspect for the symbol. |
| `declaration-relationships` | One exact subject symbol and one predicate from section 3.3.5 | Every direct relationship fact for that subject and predicate. |
| `procedure-summaries` | One exact callable symbol | Every core may-information transfer for that callable. |

There is no core `effects` fact family in v0.1. Effect profiles define separate
namespaced families under section 3.6, so a completeness claim never closes
effects merely because it closes `procedure-summaries`.

Future core sections and profiles may define additional families only by
defining the same scope and coverage operations. Non-core family identifiers
use the namespaced extension mechanism in section 3.6. A consumer MUST NOT apply
a completeness statement whose family or required coverage semantics it does
not support and MUST report the affected claim as uninterpretable.

A coverage scope MUST use artifact and symbol identity from sections 3.1 and
3.2. Display names, source text, wildcard strings, producer database IDs, and
analyzer-local query expressions MUST NOT define a core scope. A claim inherits
the enclosing semantic model's artifact selectors, compatibility constraints,
semantic-model version, and required vocabulary uses affecting the claim and
its scope. It cannot widen any of them.

#### 3.5.2 Coverage statuses

The coverage statuses are:

| Status | Normative meaning |
| --- | --- |
| `unknown` | The producer makes no assertion about whether the scoped fact set is exhaustive. Emitted facts remain positive facts; omission has no negative meaning. |
| `partial` | The producer asserts that coverage of the scope is not exhaustive. Emitted facts remain positive facts and additional facts may exist; omission has no negative meaning. |
| `complete` | The producer asserts that every fact required by the family semantics within the exact scope is emitted or semantically covered under the family's defined subsumption relation. Family-defined closed-world inference is permitted for facts not covered by that set. |

Absence of a completeness statement defaults to `unknown` for facts emitted by
an applicable model. A producer MAY state `unknown` explicitly so that a modeled
scope with no coverage determination remains distinguishable in provenance and
diagnostics. `partial` may accompany an empty fact set; it does not assert that
any particular omitted fact exists. `complete` may also accompany an empty fact
set, in which case it is an explicit closed-set assertion for that family and
scope.

Completeness is about missing facts, not extra conservative facts. When a fact
family permits over-approximation, a complete set may still be imprecise, but it
MUST cover every fact required by that family's semantics. A producer that knows
relevant behavior exists but cannot express, identify, or analyze it under the
required core or profile semantics MUST NOT claim `complete`.

#### 3.5.3 Availability is not completeness

After preserving model-discovery, validity, applicability, and interpretability
outcomes independently, a consumer that has no applicable and interpretable
model supplying either a fact or a completeness statement for a requested
family and scope MUST report effective coverage as **unavailable**.
`unavailable` is a consumer outcome, not a fourth serialized coverage status.

An unavailable scope MUST remain distinguishable from an applicable scope whose
status is `unknown`, `partial`, or `complete`. Likewise, malformed input,
inapplicability, indeterminate applicability, an unsupported required
vocabulary use, and a conflict are not coverage statuses and MUST NOT be relabeled as
`unknown` or `partial`.

#### 3.5.4 Typed limitations

A `partial` statement MUST contain at least one limitation. An explicit
`unknown` statement MAY contain limitations. A `complete` statement MUST NOT
contain a limitation.

The core limitation kinds are:

| Kind | Meaning |
| --- | --- |
| `coverage-limited` | The producer intentionally or inherently covered only part of the declared scope. |
| `input-unavailable` | Required source, binary, metadata, dependency, or other producer input was unavailable. |
| `unsupported-semantics` | Relevant semantics could not be represented or analyzed under the producer's supported vocabulary. |
| `budget-exhausted` | A deterministic resource or exploration budget ended analysis before coverage was complete. |
| `cancelled` | Generation was cancelled after the emitted facts had been established safely. |
| `producer-error` | A producer failure prevented complete coverage while leaving the emitted facts valid. |
| `other` | Another limitation applies and is explained by diagnostic metadata. |

Limitations are diagnostic evidence, not scope modifiers. They MUST be preserved
with the claim and its provenance. A consumer MUST NOT use a favorable or
unrecognized limitation to promote coverage, infer an omitted fact, or treat a
failed operation as a complete empty set. A consumer MUST report an unrecognized
limitation kind while preserving the statement's `partial` or `unknown` status.
An `other` limitation MUST include non-empty diagnostic metadata explaining the
limitation. A producer affected by cancellation or error MUST emit only facts
whose semantic validity it can still attest; if it cannot do so, it MUST NOT
emit a semantic model from that operation.

#### 3.5.5 Producer obligations for complete claims

Before asserting `complete`, a producer MUST establish coverage for the exact
artifact, family, scope, semantic-model version, identity schemes, and required
profiles named by the applicable model. It MUST account for every relevant input
and every family-defined fact that the selected semantics require.

Budget exhaustion, cancellation, stale inputs, unavailable dependencies,
unsupported relevant constructs, unresolved required identity, and unexamined
portions of the declared scope prohibit a `complete` claim. Narrowing the scope
is permitted only when the fact family's scope grammar represents that narrower
scope exactly; a producer MUST NOT hide an omission in diagnostic text or a
free-form condition.

Consumer-resolved evidence under section 3.3.6 may satisfy an explicit semantic
dependency, but it MUST NOT silently upgrade a producer's `unknown` or `partial`
statement to `complete`. A producer that makes a complete claim remains
responsible for explicitly describing every dependency required to interpret
that claim.

#### 3.5.6 Omission and negative inference

Under `unknown` or `partial`, omission never implies absence. Under `complete`,
an omitted fact may be treated as absent only when:

1. the candidate fact belongs to the same family and is contained by the exact
   claim scope;
2. artifact applicability is matched rather than indeterminate;
3. the claim and candidate use supported, comparable identity and profile
   semantics; and
4. no emitted fact covers the candidate under the family's equality or
   subsumption rules.

The v0.1 core defines no universal negated-fact record. A complete scoped set,
including a complete empty set, is the core mechanism for asserting absence.
A profile that defines explicit negative facts MUST also define their family,
scope, contradiction, and merge semantics; a consumer that lacks those required
semantics must fail closed. Such a negative fact is semantically valid only when
an applicable `complete` statement covers it; otherwise the affected model is
semantically invalid.

Closed-world inference never crosses fact-family boundaries. A complete empty
`procedure-summaries` set means there are no core may-information transfers for
that callable; it does not mean the callable cannot allocate, mutate, throw,
call, escape values, perform I/O, or have another effect. A complete empty
`declaration-relationships` set for `overrides` means that no direct `overrides`
relationship applies in that scope; it says nothing about inherited or
transitive relationships.

#### 3.5.7 Combining applicable sources

A consumer combining sources MUST first establish that the target artifacts,
fact-family semantics, and claim scopes are comparable. Claims that apply to
different artifact variants or use incompatible family or profile versions do
not combine merely because their display text is similar.

For comparable applicable sources, a consumer MUST:

1. preserve each fact, statement, limitation, and provenance separately;
2. combine positive facts using the family's equality, subsumption, and conflict
   rules;
3. report the aggregate scope as `complete` when at least one applicable source
   has a valid covering `complete` statement and all other facts and complete
   statements are compatible with it;
4. otherwise report `partial` when at least one source states `partial`; and
5. otherwise report `unknown`.

Two or more `partial` sets MUST NOT be promoted to `complete` merely because
their union appears large or their omissions appear complementary. An
`unknown` or `partial` source does not by omission contradict a compatible
complete source. Additional conservative facts may reduce precision without
reducing coverage when the family permits them.

Family-defined negative inference is evaluated against the aggregate compatible
fact set. Once sources are combined, a consumer MUST NOT infer absence from one
source while ignoring a positive fact retained from another.

Within one semantic model, incompatible complete statements or facts that
contradict a complete claim under the family's closed-set rules are semantic
invalidity. Across otherwise valid sources, such a contradiction makes the
affected aggregate scope uninterpretable. A consumer MUST NOT choose a winner
by producer priority, trust score, input order, or the apparently stronger
coverage status. It also MUST NOT construct a broader complete claim from
narrower scopes unless the fact family defines composition and those scopes
provably cover the broader scope without gaps.

#### 3.5.8 Versions, variants, and conditions

Completeness statements do not contain free-form version ranges, feature
expressions, runtime predicates, or call-path conditions. Version and artifact
variation belongs in the selectors and compatibility constraints of section
3.1. If the same package coordinate has different facts or completeness under
different versions, build features, platforms, or runtime environments, the
producer MUST use semantic models whose applicability separates those cases.

A profile may define a conditional coverage scope only as required semantics,
including a deterministic evaluation and comparison procedure. If the consumer
cannot interpret the condition or establish its outcome, the claim is
uninterpretable or its applicability is indeterminate; the consumer MUST NOT
assume the favorable branch.

#### 3.5.9 Confidence, provenance, and soundness

Coverage status is categorical and MUST NOT be interpreted as a probability,
confidence score, fact ranking, or proof certificate. `unknown` and `partial`
do not mean that emitted facts are less likely to be correct, and `complete`
does not mean that the producer or consuming analysis has been independently
verified as sound.

The v0.1 core does not define quantitative confidence. A profile MAY add
confidence metadata only if ignoring it cannot change the core facts,
completeness, or negative inference. Provenance and integrity under section 3.7
may inform an operator's trust policy, but accepting or rejecting a producer
does not rewrite the producer's reported coverage status.

### 3.6 Effects, profiles, and extensions

CSMI uses profiles and extensions to add semantic domains without forcing every
consumer to implement them. A standard profile is defined and versioned under
CSMI governance. A vendor extension is defined and versioned by the authority
that owns its namespace. Both are optional capabilities for a core CSMI
implementation; an individual use may nevertheless be required to interpret
the semantic units it affects.

The v0.1 core defines no generic effect fact. In particular, `allocation`,
`mutation`, `escape`, `invocation`, I/O, network, ownership, concurrency,
typestate, and taint are not core vocabulary values. A producer MUST NOT encode
one of them as an opaque core `effect` string. This keeps core transfer
completeness independent from analysis domains whose targets and closed-world
meaning differ.

This decision does not make those concepts unimportant. It requires each
effect vocabulary to define enough meaning for two independent analyzers to
agree on what its facts assert and omit.

#### 3.6.1 Effect-profile requirements

An effect profile or extension MUST define a namespaced fact family rather than
adding a generic tag to a procedure summary. Its definition MUST specify:

- the exact callable or other core identity to which each fact applies;
- whether a fact means `may`, `must`, or another precisely defined modality;
- every operand and target, using core symbols, boundary locations, or a
  profile-defined identity with deterministic comparison rules;
- the invocation, lifetime, reachability, or temporal boundary at which the
  effect is observed;
- fact equality, conflict, conservative over-approximation, and merge rules;
- interaction, if any, with core may-information transfers;
- a fact-family coverage scope and the exact closed-world inference licensed by
  `complete` under section 3.5; and
- realistic positive cases and near misses in its conformance material.

No effect fact implies a core transfer, and no core transfer implies an effect,
unless a vocabulary use declared `required` explicitly defines that
relationship. Likewise, a complete effect-family set does not assert purity
outside that exact family.

The four effects considered for v0.1 remain profile candidates for these
reasons:

| Candidate | Required profile boundary |
| --- | --- |
| Allocation | What is created, whether freshness is asserted, which result or reachable region exposes it, and what lifetime is relevant. |
| Mutation | Which pre-existing abstract location may change and what caller-visible observation counts as mutation. This is the strongest candidate for a first standard effect profile because it can reuse section 3.4 boundary locations. |
| Escape | The reachability or ownership boundary crossed, the escaping source, and whether retention, publication, or transfer of control is asserted. |
| Invocation | Whether the target is an exact callable or callback-valued location, and the dispatch, cardinality, timing, argument, result, exception, and asynchronous semantics that are and are not asserted. |

An immediate exceptional exit is also not inferred merely because section 3.4
defines an `exception` output root. A transfer to that root says that input
information may influence an exception value; a constant thrown value can have
an exceptional effect without such a transfer. A future effect profile may
model that distinction.

Security taint is a separate analysis domain rather than an effect synonym. A
taint profile must define sources, sinks, sanitizers, barriers, propagation,
threat-model scope, and completeness while reusing core boundary locations
where applicable.

#### 3.6.2 Vocabulary classes and namespaces

Standard profiles and vendor extensions use one identifier space of lowercase
ASCII dotted names. Each label MUST begin and end with an ASCII letter or digit,
MAY contain interior hyphens, and MUST NOT be empty. Identifiers are compared by
exact code-point equality; consumers MUST NOT case-fold, normalize, or compare
only a suffix.

The `csmi.` prefix is reserved for standard profiles assigned by this
specification or a future CSMI registry. A producer MUST NOT mint a `csmi.` name.
The `example.` and `org.example.` prefixes are reserved for non-distributable
examples and conformance fixtures. They MUST NOT appear in a distributable
pack.

A vendor extension MUST begin with a reverse-DNS namespace derived from a DNS
name controlled by its publisher. For example, the publisher controlling
`brokk.ai` may define `ai.brokk.bifrost.generator-rules`. A publisher MUST NOT
use a domain it does not control or a bare, collision-prone prefix such as
`brokk.bifrost`.

Namespace ownership distinguishes a standard profile from a vendor extension;
it does not make a use optional or required. Standard-profile support is not
implied by core conformance, and a vendor extension is not inherently less
trustworthy or less portable. Consumers SHOULD report support as exact
identifier-and-version pairs.

An identifier MUST NOT be repurposed for incompatible semantics. Standardizing
a vendor extension requires either a new `csmi.` identifier with a normative
mapping or an explicit transfer of namespace governance; consumers MUST NOT
assume equivalence from similar names.

#### 3.6.3 Versions and schemas

Every vocabulary definition and use MUST identify one exact, non-empty version.
Versions are opaque identifiers for comparison by default. Publishers SHOULD
use [Semantic Versioning 2.0.0](https://semver.org/spec/v2.0.0.html) when its
compatibility model fits, but a consumer MUST NOT infer semantic compatibility,
version ranges, or upgrade safety merely from SemVer precedence. Supporting
`1.2.0` does not support `1.2.1` unless the vocabulary definition supplies a
normative compatibility rule that the consumer implements.

Every vocabulary with serialized payload MUST identify a JSON Schema Draft
2020-12 schema by an absolute URI conforming to
[RFC 3986](https://www.rfc-editor.org/rfc/rfc3986). The URI identifies the
schema; it does not require network retrieval. A pack may carry the schema or
bind it by integrity metadata under section 3.7. Consumers MUST NOT fetch or
execute arbitrary schema content merely because an unknown vocabulary names a
URI.

Schema validation proves only payload structure. It does not prove that a
consumer implements the vocabulary's semantics. A consumer MUST NOT treat
successful schema validation, a matching schema URI, or preservation of opaque
payload as semantic support.

A vocabulary definition MUST publish, for each version:

1. its exact identifier, version, governance class, and schema identifier;
2. its semantic vocabulary and every permitted attachment point;
3. all profile dependencies and their exact versions;
4. affected fact families, scope grammars, equality, conflict, merge, and
   completeness rules;
5. requiredness and unsupported-vocabulary behavior for each kind of use; and
6. semantic conformance cases sufficient for an independent implementation.

A change to payload shape requires a new schema identity and vocabulary
version. A change to semantic meaning, completeness, comparison, or conformance
obligations requires a new vocabulary version even when payload shape is
unchanged. An editorial change that changes neither need not create a version.

#### 3.6.4 Vocabulary uses and requiredness

Every vocabulary use MUST identify the exact vocabulary and version, declare
`optional` or `required`, and identify the semantic units it affects. The
affected unit is one of:

- a namespaced fact family and one family-defined scope;
- a core fact that contains a value at an explicitly delegated profile slot;
  or
- a namespaced attachment associated with an exact core identity or fact under
  a schema-defined attachment point.

Requiredness belongs to the use, not permanently to the vocabulary. Throughout
the preceding sections, the shorthand "required profile" means a profile use
that MUST be declared `required` for the affected semantic unit under this
section; it never makes the vocabulary inherently required. One model
may use a profile only for ignorable annotations while another relies on the
same profile version to interpret a projection, compatibility condition, or
fact family. A declaration that fails to identify the affected semantic units
is semantically invalid because a consumer cannot fail closed at the correct
boundary.

A use is `required` when ignoring it could change interpretation,
applicability, symbol or location binding, fact equality, conflict,
completeness, or negative inference for an affected unit. A producer MUST NOT
label such a use `optional`. All dependencies needed to interpret a required
use are also required for that affected unit.

Every dependency named by a vocabulary definition MUST appear as its own
declared vocabulary use with an exact version and affected units. A consumer
MUST NOT infer a transitive dependency declaration from documentation or fetch
one from a schema URI. A dependency of a required use is required for the same
affected units; if an optional use or any of its dependencies is unsupported,
the complete optional use is skipped.

A use is `optional` only when removing the complete use and all of its payload
leaves every core fact, supported non-core fact, applicability result,
completeness statement, and negative inference unchanged. Optional does not
mean that an unsupported consumer understands the extension-owned facts; it
means those facts may be omitted from that consumer's interpretation without
corrupting the remaining model.

#### 3.6.5 Permitted extension surfaces

A profile or extension MAY add semantics in exactly these ways:

1. define a new namespaced fact family that references core artifact, symbol,
   declaration, boundary-location, or other defined identities;
2. supply a value at a core slot that explicitly delegates its vocabulary,
   such as an identity scheme, intrinsic type, projection scheme,
   compatibility condition, or relation kind; or
3. place namespaced data in an explicit extension attachment point defined by
   the normative serialization schema.

The first form is preferred for independently queryable analysis facts because
it gives the family its own scope, merge, and completeness contract. An
attachment is appropriate only when its target identity and removal behavior
are defined precisely.

An extension MUST NOT add arbitrary properties directly to a core object,
replace a core enum value with a namespaced string unless that slot explicitly
delegates its vocabulary, reinterpret a core field, or override a core fact.
The JSON serialization remains closed by default under section 4.1. Section
2.5 defines the concrete extension container without changing these semantic
restrictions.

#### 3.6.6 Unknown and unsupported vocabulary

Vocabulary payload without a corresponding declared use is semantically
invalid. A declared use with an unrecognized identifier or unsupported exact
version is unsupported vocabulary. A consumer MUST report the identifier,
version, requiredness, and affected units; it MUST NOT guess semantics from the
name, schema, payload keys, or a nearby supported version.

For unsupported `optional` vocabulary, the consumer MAY ignore the affected
extension-owned facts or attachments while continuing to interpret unaffected
core and supported facts. If it reserializes or proxies the model, it SHOULD
preserve the declaration and opaque payload unchanged. A request for the
unsupported extension-owned family remains unsupported or uninterpretable; it
MUST NOT be reported as an empty or unavailable supported family.

For unsupported `required` vocabulary, every affected unit and every fact or
claim that depends on it is uninterpretable. Unaffected semantic units remain
usable when the declared affected boundary proves that they are independent. A
required use that affects artifact applicability, an identity scheme, or a
shared projection may therefore make many dependent facts uninterpretable. A
consumer MUST NOT downgrade the use to optional, drop the payload, or relabel
the outcome as inapplicable, `unknown`, `partial`, or complete-empty.

Malformed payload under a supported vocabulary is structural or semantic
invalidity as appropriate, not unsupported vocabulary. A structurally valid
payload whose required semantic invariants fail is semantically invalid.

#### 3.6.7 Completeness and source combination

Every namespaced fact family MUST satisfy the family-definition requirements in
section 3.5.1. Its identity is the tuple of defining vocabulary identifier,
exact vocabulary version, and a stable family key assigned within that
vocabulary version. A vocabulary that defines more than one family MUST assign
distinct keys and define each family independently. Claims with different tuple
components do not combine unless an implemented normative mapping establishes
equal family and scope semantics.

Core completeness never closes a profile family, and profile completeness never
closes a core or different profile family. In particular, a complete
`procedure-summaries` scope says nothing about mutation, escape, invocation,
taint, or another effect family. A complete profile-owned scope permits only
the negative inference defined by that profile.

Ignoring an optional use MUST NOT strengthen any remaining completeness status
or remove a limitation. An unsupported required family or coverage rule makes
the affected claim uninterpretable under sections 3.5.1 and 3.5.3; it does not
turn the claim into `unknown` or `partial`.

When combining applicable sources, consumers MUST preserve each vocabulary
declaration and exact version with its facts and provenance. Facts from
incomparable versions remain separate. A conflict under an implemented profile
uses that profile's conflict rule and the fail-closed aggregation rules in
section 3.5.7; source priority and apparent version recency do not select a
winner.

#### 3.6.8 Guidance for Bifrost generator rules

Bifrost-specific generator rules SHOULD begin as a vendor extension under a
name such as `ai.brokk.bifrost.generator-rules`, not in core and not under the
reserved `csmi.` namespace. The extension should define a namespaced fact
family, exact version, schema, affected scope, equality, conflict, merge, and
completeness semantics.

Generator facts MUST identify declarations, callables, operands, and boundary
locations through resolver-proven CSMI identities. Display names, regular
expressions over source text, producer database IDs, and analyzer-local query
expressions are not portable identity. A use is required whenever a model's
interpretation or completeness depends on the generator semantics; a
standalone advisory family may be optional when removing it leaves all other
semantics unchanged.

Promotion to a standard profile should require an analyzer-neutral contract,
an independent producer or consumer, stable conformance fixtures, and
demonstrated equality and completeness behavior. Promotion MUST use a new
`csmi.` identifier or a normative mapping; it MUST NOT silently repurpose the
vendor identifier.

#### 3.6.9 Explicit non-goals

The v0.1 extension mechanism does not define a registry, transport protocol,
automatic schema download, executable plug-in format, trust score, arbitrary
JSON property escape hatch, universal effect lattice, or compatibility rule
for different vocabulary versions. Those facilities must not be inferred from
an identifier or schema URI.

#### 3.6.10 Standard profile definitions

Standard profile definitions are versioned normative resources next to this
specification. CSMI 0.1 currently assigns the JavaScript, TypeScript, and Node
profile family in the
[JavaScript, TypeScript, and Node profile definition](https://csmi.brokk.ai/profiles/javascript-typescript-node/).
It defines resolver-proven runtime and declaration identity, Node builtin alias
rules, runtime-to-declaration mappings, and Node/TypeScript compatibility
constraints without adding language-specific properties to the core schema.

Implementing CSMI core does not imply implementing that family. A document that
uses one of its identity or compatibility semantics declares the exact
vocabulary use as required and fails closed under section 3.6.6 when unsupported.

### 3.7 Manifest, provenance, and canonicalization

A CSMI pack is a content-addressed logical set consisting of one root manifest
and every resource named by that manifest. The manifest commits to the exact
resource bytes, assembly identity, and licensing envelope. It does not move
semantic applicability, completeness, or required-vocabulary declarations away
from the semantic documents they govern.

This separation has three consequences:

1. a semantic document remains interpretable without its original pack when its
   referenced resources are otherwise available;
2. changing packaging metadata does not rewrite fact provenance, although it
   does create a different pack; and
3. a digest or signature establishes byte identity, not semantic correctness,
   applicability, completeness, producer trust, or analyzer soundness.

#### 3.7.1 Semantic-document and manifest responsibilities

Every semantic document MUST carry or reference within that document:

- its semantic-model version, serialization version, and schema identity;
- each semantic model's artifact selectors and compatibility constraints;
- every vocabulary use required by section 3.6;
- its semantic facts and scoped completeness statements; and
- the semantic-producer provenance required by section 3.7.2.

The root pack manifest MUST contain:

- one exact pack-format version;
- one pack-assembler identity and exact version;
- one default pack license expressed as a valid SPDX license expression;
- an unordered, non-empty set of resource descriptors; and
- at least one resource whose role is `semantic-document`.

The manifest MAY contain an optional deterministic creation timestamp, license
overrides for individual resources, and exact predecessor-pack references. If
present, the creation timestamp MUST be an RFC 3339 UTC instant. All manifest
fields participate in the pack digest. Producers seeking reproducible output
SHOULD omit wall-clock creation time or derive it from a deterministic build
input such as `SOURCE_DATE_EPOCH`. A publication or upload time is transport
metadata and MUST NOT be inserted into an existing manifest.

Artifact selectors, compatibility constraints, vocabulary uses, completeness
summaries, and semantic facts MUST NOT be duplicated in the manifest as
authoritative claims. Such duplication would create conflicting sources of
truth. A future manifest index may accelerate discovery only if its
non-authoritative status and consistency validation are defined by a newer
pack-format version.

A standalone semantic document is a valid semantic input but is not, by itself,
a v0.1 distributable pack. Packaging it supplies a byte-integrity and licensing
envelope without changing its meaning.

#### 3.7.2 Semantic-producer provenance

Provenance identifies who or what established a fact and the evidence boundary
under which it was established. It is not confidence, trust, authorship credit,
or pack assembly metadata.

Every semantic document MUST define at least one provenance record. A record
MUST contain:

1. a globally unambiguous semantic-producer identifier represented by an
   absolute URI that need not be dereferenced;
2. the producer's exact, non-empty version or process revision;
3. one generation method from the core vocabulary below; and
4. the material inputs required by that method, each with stable identity and
   an exact digest when bytes or canonical content were available.

The core generation methods are:

| Method | Meaning |
| --- | --- |
| `source-analysis` | Facts were derived by analyzing source content. |
| `binary-analysis` | Facts were derived by analyzing compiled or packaged program content. |
| `metadata-conversion` | Facts were converted from a declaration, index, model, or metadata format. |
| `manual-authoring` | Facts were established through a maintained human-authoring process. |
| `composition` | Facts were selected, mapped, or combined from identified semantic inputs. |
| `mixed` | More than one of the preceding methods materially established the facts. |
| `other` | Another method applies and is explained by non-empty diagnostic metadata. |

An input record MUST identify its role, such as target artifact, source
artifact, binary artifact, metadata, or predecessor semantic pack. Artifact
inputs SHOULD reuse section 3.1 identity and digest semantics. A predecessor
pack MUST be identified by its pack digest. Source, binary, and metadata inputs
that materially justify a `complete` claim MUST use exact content evidence; a
coordinate, branch name, mutable URL, or creation timestamp alone is
insufficient.

Manual authoring need not invent a byte input, personal identity, or wall-clock
time. It MUST identify a stable maintained process and exact revision, such as a
reviewed model repository revision or policy version. Composition MUST retain
the input semantic-document content digests or pack digests and MUST NOT replace
their provenance with the composer's identity. A v0.1 semantic-document content
digest is SHA-256 over that document's normalized JCS bytes; when the document
is a pack resource, it is the same digest recorded by its resource descriptor.

Every fact and completeness statement MUST resolve to at least one provenance
record. A document MAY declare one default record only when that record applies
to every otherwise unannotated fact and claim in the document. Mixed-origin
documents MUST attach narrower provenance references wherever the default would
be false or incomplete. Consumers combining sources MUST preserve all resolved
records independently under sections 3.3.7, 3.5.7, and 3.6.7.

A creation timestamp and invocation identifier MAY be recorded for auditability
but MUST NOT be required for semantic interpretation. If present, a timestamp
MUST be an RFC 3339 UTC instant. A consumer MUST NOT use recency, producer
version, or generation method to select a winner between conflicting facts.

#### 3.7.3 Pack assembly and licensing

The pack assembler selects bytes and constructs the manifest. Its record MUST
contain a globally unambiguous absolute-URI identifier and exact version or
process revision. Assembly does not establish semantic facts. If an assembler
rewrites, maps, deduplicates under semantic equality, or otherwise changes a
semantic document's claims, that operation is semantic `composition` and MUST
also appear in the document provenance.

An optional predecessor-pack reference means that the assembler derived this
pack from an exact prior pack. It MUST contain the predecessor pack digest and
MUST NOT substitute for resource or fact provenance. Mutable tags, registry
coordinates, filenames, and URLs are not predecessor identity.

The default pack license and every resource override MUST be valid
[SPDX license expressions](https://spdx.github.io/spdx-spec/v3.0.1/annexes/spdx-license-expressions/).
Every custom `LicenseRef` used by one of those expressions MUST resolve to
exactly one corresponding `license-text` resource under section 3.7.4. A
resource without an override inherits the pack default. Pack licensing
describes permission for the pack resources; it MUST NOT be interpreted as the
license of the modeled target artifact.

#### 3.7.4 Resource descriptors and multi-file packs

Each resource descriptor MUST contain:

- one normalized logical path;
- one core resource role;
- one exact media type;
- the exact non-negative byte size; and
- one SHA-256 digest over the exact resource bytes.

A descriptor MAY additionally carry the resource's SPDX license override. A
`vocabulary-schema` descriptor MUST also bind one absolute schema-identifier
URI. A `license-text` descriptor MAY bind one exact custom SPDX `LicenseRef`.
These bindings MUST NOT appear on another resource role. No other optional
descriptor metadata is defined in v0.1.

The v0.1 core roles are:

| Role | Meaning |
| --- | --- |
| `semantic-document` | A self-describing CSMI semantic-model document. |
| `vocabulary-schema` | A schema named by a standard profile or vendor extension. |
| `license-text` | License text required by a `LicenseRef` or supplied for review. |
| `notice` | Human-readable attribution or legal notice. |
| `auxiliary` | Non-authoritative content that may be ignored unless a semantic document references it through defined vocabulary semantics. |

Schema-identifier bindings MUST be unique within a pack. The bound schema's
top-level `$id` MUST equal the descriptor binding by exact code-point equality;
successful parsing or a filename match is insufficient. A semantic document
that names that schema URI can therefore resolve to exact local bytes without
network retrieval.

Custom-license bindings MUST be unique within a pack. Each custom `LicenseRef`
in the default license or a resource override MUST equal one such binding
exactly. An unbound `license-text` resource is permitted as review material but
does not satisfy a `LicenseRef`. The content of a bound license text is not
interpreted as an SPDX expression and does not recursively license itself.

A logical path uses `/` separators, is relative to the pack root, and is
compared by exact code-point equality. It MUST be non-empty and normalized,
MUST NOT contain an empty, `.` or `..` segment, and MUST NOT begin with `/`, a
URI scheme, a drive prefix, or another platform-specific root. Backslashes,
NUL, percent-encoded traversal, and Unicode characters that are not NFC are
invalid. Descriptor paths MUST be unique. Producers SHOULD avoid paths that
differ only by Unicode normalization or case because common materializations
cannot preserve those distinctions safely.

The manifest itself is the root of the content-addressed graph and MUST NOT list
itself as a resource. Resource descriptors contain no retrieval URL. A transport
maps logical paths or digests to bytes outside the semantic model.

The `semantic-document` media type for the v0.1 JSON serialization is
`application/vnd.csmi.semantic-model.v0.1+json`; the root-manifest media type is
`application/vnd.csmi.pack-manifest.v0.1+json`. A vocabulary schema uses
`application/schema+json`. Other roles MUST state an exact applicable media
type rather than relying on a filename extension.

Multiple semantic documents may refer to one another only through CSMI artifact,
symbol, vocabulary, provenance, or other semantics defined by this
specification. A filename, descriptor order, JSON array position, or transport
location MUST NOT become semantic identity or source priority.

#### 3.7.5 Canonical JSON and deterministic sets

The root manifest and every JSON resource in a content-addressed v0.1 pack MUST
be serialized in the JSON Canonicalization Scheme defined by
[RFC 8785](https://www.rfc-editor.org/rfc/rfc8785). Accordingly, the input MUST
be valid I-JSON: object member names are unique, strings contain valid Unicode,
and numbers satisfy the JCS representation constraints. JSON Schema validation
alone does not establish canonical form.

JCS canonicalizes objects and primitive values but deliberately preserves array
order. Before JCS serialization of a root manifest or semantic document, a CSMI
producer MUST normalize CSMI-defined arrays according to their semantic kind:

- ordered sequences, including callable parameters, tuple and type arguments,
  projection steps, and other constructs whose semantics assign an index or
  traversal order, retain their defined order;
- set-valued collections, including resource descriptors, fact collections,
  completeness-statement collections, vocabulary uses, provenance records, and
  predecessor-pack references, are recursively normalized, have byte-identical
  duplicate entries removed, and are sorted lexicographically by the unsigned
  UTF-8 bytes of each entry's JCS representation; and
- a profile or extension that introduces an array MUST define whether it is an
  ordered sequence or set and any semantic normalization required before this
  generic rule is applied.

Another JSON resource, such as a vocabulary schema, MUST still use JCS bytes,
but its defining format owns its array semantics. CSMI MUST NOT reorder an array
in that resource unless that format declares the ordering irrelevant and a
deterministic normalization rule applies.

Section 2.5 defines the concrete JSON mapping and labels every core array as
ordered or set-valued. The serialization prohibits alternate default-valued
encodings where the distinction matters. Semantic subsumption does not make two
facts byte duplicates and MUST NOT be used to remove one during
canonicalization.

Readability whitespace shown in specifications and examples is not part of
canonical pack bytes. A consumer verifying a descriptor hashes the supplied raw
bytes; it MUST NOT parse and reserialize non-canonical input to make a digest
match. This permits integrity verification before semantic interpretation.

#### 3.7.6 Content addressing and integrity verification

The v0.1 resource digest algorithm is SHA-256. A digest value is the lowercase
64-character hexadecimal encoding of the hash of the exact resource bytes.
The declared byte size is the number of those bytes, not characters, code
points, or decoded JSON units.

The pack digest is SHA-256 over the RFC 8785 canonical UTF-8 bytes of the root
manifest after applying section 3.7.5. The manifest MUST NOT contain its own
digest, because doing so would create a self-reference. A pack reference is the
tuple of algorithm `sha-256` and this digest value; display syntax such as
`sha256:<hex>` is not an additional identity scheme.

To consume a pack, an implementation MUST:

1. validate the manifest structure and semantic invariants, including safe
   paths and unique descriptors;
2. compute its pack digest and compare it with any expected pack digest supplied
   by the caller or transport;
3. obtain each described resource without resolving outside the pack boundary;
4. compare its exact byte size and SHA-256 digest before parsing it;
5. validate canonical JSON, schema, and semantic conformance as applicable; and
6. only then expose semantic facts for applicability and interpretation.

A digest or size mismatch, missing described resource, unsafe resolution, or
expected-pack-digest mismatch is an **integrity failure**. The pack MUST NOT be
partially applied. It MUST NOT be relabeled as an empty model, unknown or partial
coverage, inapplicability, unsupported semantics, or a producer limitation.

If no expected pack digest is supplied, a consumer can still establish the
computed pack identity and internal agreement between the manifest and resource
bytes. That does not authenticate the manifest or its producer. Likewise, an
exact digest says nothing about whether the semantic claims are correct.

#### 3.7.7 Detached signatures and attestations

Signatures and attestations are external to the logical v0.1 pack. They MUST NOT
be embedded in the root manifest or listed as pack resources when they sign that
same pack, because either form creates self-reference or makes adding a signer
change the subject's identity.

A future signature or attestation envelope can bind the pack without redesigning
it by naming the pack digest as its subject and authenticating both that digest
and an unambiguous payload type. Formats such as in-toto attestations with DSSE
are compatible with this layering, but v0.1 does not mandate a signature format,
key discovery mechanism, identity provider, transparency log, or trust policy.

Verifying an external signature establishes only the claims defined by that
attestation and its verifier policy. It MUST NOT silently promote artifact
applicability, interpret unsupported vocabulary, change completeness, or resolve
conflicting semantic facts.

#### 3.7.8 Transport and registry boundary

Transport, archive encoding, compression, discovery, dependency resolution,
registry APIs, upload and download, authentication, access control, retention,
mirroring, and mutable tags are out of scope for v0.1.

A directory, archive, OCI artifact, HTTP service, package registry, or another
mechanism may carry the same logical pack. The transport MUST preserve the exact
manifest and resource bytes or produce a different pack digest. Additional
transport files and detached attestations are outside the logical pack and MUST
NOT be interpreted as resources unless a different manifest explicitly
describes them.

A transport MAY advertise a pack digest or map it to a location, but a mutable
name or URL MUST NOT replace digest verification. Consumers MUST apply resource
limits and safe extraction rules appropriate to the transport; the absence of a
v0.1 archive format is not permission for path traversal, symlink escape,
decompression bombs, or unbounded retrieval.

#### 3.7.9 Combining packs and explicit non-goals

Manifest order, pack order, assembler identity, creation time, license, and
transport location confer no semantic precedence. Consumers combine applicable
facts and claims using their family rules while preserving per-source provenance
and pack/resource digests. A conflict remains invalid or uninterpretable under
the relevant semantic section; selecting the newer or more trusted pack is an
observable operator policy outside CSMI semantics.

The v0.1 manifest does not define a semantic query index, authoritative
completeness summary, dependency solver, registry coordinate, mutable release
channel, SBOM, signature format, trust score, or license for the modeled target
artifact.

## 4. Conformance

Conformance has six independent dimensions:

| Dimension | Question |
| --- | --- |
| Structural validity | Does the document conform to the declared serialization schema? |
| Semantic validity | Do its references and semantic claims satisfy the specification's invariants? |
| Applicability | Does it match the exact artifact and variant under analysis? |
| Interpretability | Does the consumer support all semantics required to interpret it correctly? |
| Coverage | Is the requested fact-family scope unavailable, unknown, partial, or complete? |
| Content integrity | Do the manifest, any expected pack digest, and every described resource agree byte-for-byte? |

A successful result in one dimension MUST NOT be reported as proof of another.
In particular, structurally valid JSON is not necessarily semantically valid,
applicable, or interpretable.

### 4.1 Structural conformance

A conforming JSON document MUST validate against the normative schema selected
by its version. The schema MUST reject unknown core object fields using JSON
Schema's closed-object facilities. Every document under `fixtures/valid/` MUST
validate, every document under `fixtures/invalid/` MUST be rejected, and every
document under `fixtures/semantic-invalid/` MUST validate structurally before
its named semantic violation is considered.

### 4.2 Semantic conformance

A conforming implementation MUST preserve the meaning defined by this
specification. In particular:

* a missing fact MUST NOT imply that behavior is absent;
* incompleteness MUST remain distinguishable from an explicit negative claim;
* unknown optional extensions MUST NOT silently change core semantics; and
* producers MUST be distinguishable from the artifact whose semantics they
  describe.

Semantic validation includes at least reference existence and scope, uniqueness
of local handles and family scopes, artifact and profile comparison, declaration
category and descriptor compatibility, contiguous callable positions, boundary
locations valid for the referenced callable shape, provenance resolution,
vocabulary-use resolution, completeness conflicts, SPDX expressions, PURL and
VERS canonicality, Unicode NFC path normalization, and JCS bytes and set order.
Passing JSON Schema MUST NOT be reported as proof that any of these checks
succeeded.

### 4.3 Independence requirement

Two independently implemented consumers MUST be able to assign the same meaning
to a core CSMI fact without using producer source code, producer internal
serialization, hidden side channels, or analyzer-specific name parsing.

### 4.4 Inconclusive and unsupported outcomes

A consumer MUST NOT collapse malformed input, semantic invalidity,
inapplicability, an unsupported version, unsupported required semantics,
incomplete coverage, or an integrity failure into a model with no facts. Each
condition MUST remain distinguishable from a complete claim that modeled
behavior is absent.
