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
defined by a required CSMI profile. A range with no specified comparison
procedure is semantically invalid; merely accepting its URI syntax is not
sufficient.

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
under the applicable completeness claim rather than mint an unstable ID.

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
rule or required profile says so.

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
presentation metadata unless a required profile gives it resolver semantics.
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
: A type atom defined by a required, namespaced, versioned profile, such as a
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
profile-defined identifier; a consumer that does not support a required
intrinsic profile cannot interpret the affected type fact. Arrays, tuples,
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
vocabulary or a required profile. The alias remains a distinct declaration;
its presence does not make the alias symbol and target symbol identical.

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
binary compatibility. A producer MUST use a required profile when those
language-specific consequences are necessary to interpret a semantic fact.

Relationship objects and type expressions MAY refer across artifact scopes.
Ownership MUST NOT. A consumer lacking comparable identity evidence for an
external endpoint cannot use the affected relationship to establish resolution.

#### 3.3.6 Optional and consumer-resolved declarations

Declarations are an optional fact family. A producer MAY omit declaration facts
that no other emitted semantic fact needs. Absence remains unknown unless an
applicable completeness claim proves the declaration fact is absent.

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
completeness claim under section 3.5; absence of an unlisted relationship is not
enough. A reference to a declaration-defined aspect with neither embedded facts
nor an explicit consumer-resolved dependency is semantically invalid.

A consumer MAY satisfy a consumer-resolved dependency from its own declaration
index only after establishing artifact applicability and symbol-scheme support.
It MUST map the local evidence through a supported identity scheme and every
required profile into the requested CSMI declaration aspect, then compare that
aspect using this section's structural and semantic rules. Display-name
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
completeness or explicit negative claim covers that fact.

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
| Transfer meaning | Treat a transfer as directional may-flow unless a separately defined relation kind proves necessary. | #5 |
| Completeness scope | Define completeness independently for each fact family rather than as a single pack-wide flag. | #6 |
| Core effects | Keep only broadly portable effect concepts in core; express specialized domains as versioned profiles. | #7 |
| Extension requirement | Make required extensions explicit so consumers can fail closed for affected facts instead of ignoring them. | #7 |
| Canonicalization | Prefer deterministic producer requirements and a defined content address; defer broad canonical JSON policy only if it is unnecessary for integrity. | #8 |
| Distribution | Exclude transport and registry protocols from v0.1. | #8 |
