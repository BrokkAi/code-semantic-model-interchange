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
The JSON serialization remains closed by default under section 4.1. Issue #9
will define the concrete extension container and schema composition without
changing these semantic restrictions.

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

### 3.7 Manifest, provenance, and canonicalization

Defines the pack envelope, its applicability and provenance claims, integrity
mechanism, and deterministic representation requirements.

## 4. Conformance

Conformance has five independent dimensions:

| Dimension | Question |
| --- | --- |
| Structural validity | Does the document conform to the declared serialization schema? |
| Semantic validity | Do its references and semantic claims satisfy the specification's invariants? |
| Applicability | Does it match the exact artifact and variant under analysis? |
| Interpretability | Does the consumer support all semantics required to interpret it correctly? |
| Coverage | Is the requested fact-family scope unavailable, unknown, partial, or complete? |

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
| Canonicalization | Prefer deterministic producer requirements and a defined content address; defer broad canonical JSON policy only if it is unnecessary for integrity. | #8 |
| Distribution | Exclude transport and registry protocols from v0.1. | #8 |
