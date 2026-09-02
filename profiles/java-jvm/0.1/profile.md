# Java/JVM interoperability profiles 0.1

This profile family defines four exact standard vocabularies:

| Identifier | Version | Schema | Purpose |
| --- | --- | --- | --- |
| `csmi.java-source-identity` | `0.1` | `java-source-identity.schema.json` | Resolver-proven Java, Kotlin, or Scala source declaration identity. |
| `csmi.jvm-binary-identity` | `0.1` | `jvm-binary-identity.schema.json` | JVM class-file identity and selected artifact variant. |
| `csmi.java-jvm-mapping` | `0.1` | `java-jvm-mapping.schema.json` | Evidence-bearing source-to-binary mapping facts. |
| `csmi.jvm-compatibility` | `0.1` | `jvm-compatibility.schema.json` | Runtime, class-file, language-metadata, and variant constraints. |

Each schema is JSON Schema Draft 2020-12 and has an absolute schema identity.
Schema validity proves payload shape only. It does not prove artifact
applicability, identity equality, mapping evidence, compatibility, completeness,
or consumer support.

This profile reuses the [Java Language Specification](https://docs.oracle.com/javase/specs/jls/se25/html/jls-8.html#jls-8.4.2)
declaration-signature rules, the [Java Virtual Machine Specification](https://docs.oracle.com/javase/specs/jvms/se25/html/)
class-file names and descriptors, the [JAR File Specification](https://docs.oracle.com/en/java/javase/25/docs/specs/jar/jar.html#multi-release-jar-files)
multi-release selection rules, and the registered PURL and VERS procedures.
Those standards remain authoritative
for their own syntax and behavior; this profile defines only their CSMI
identity, applicability, mapping, and fail-closed composition.

## Common obligations

The four vocabularies are independent exact-version capabilities. A semantic
model MUST declare every vocabulary it uses through `vocabularyUses`, including
the schema URI, exact `0.1` version, requiredness, and affected units. A use MUST
be `required` whenever ignoring it could change artifact applicability, symbol
binding, mapping, fact equality, or completeness. Unsupported required uses make
the affected units uninterpretable. Unsupported optional uses may be preserved
or skipped only within their declared boundary.

Consumers MUST NOT infer identity or source/binary equivalence from display
names, source text, JVM descriptor resemblance, external moniker text,
producer-local IDs, traversal order, or a nearby profile version. A structurally
valid payload whose invariants below fail is semantically invalid. A supported
payload with insufficient comparison evidence is indeterminate. Those outcomes
MUST remain distinct.

The profile schemas serialize canonical components for conformance and
profile-owned facts. In a CSMI semantic document, source and binary symbol keys
use the core `symbols` structure with the corresponding `scheme` and
`schemeVersion`; conforming implementations derive their core descriptor paths
from these same canonical components.

## Java source identity

`csmi.java-source-identity` identifies declarations resolved by a Java, Kotlin,
or Scala front end. Its payload is compared as the tuple of exact profile
version, language, package segments, owner path, declaration variant, and its
identity-bearing signature fields. `origin` is metadata and is not an identity
component. A generated or synthetic declaration's `generation.stableKey`
participates only when the resolver-visible tuple would otherwise collide; the
origin and generation-kind labels are metadata. Strings are compared by exact
Unicode scalar sequence after the source language's escape processing.
Producers MUST NOT case-fold, silently Unicode-normalize, or combine package or
owner segments into a display FQN.

The corresponding core descriptor path consists of one `namespace` descriptor
per package segment, one `type` descriptor per owner, and a final descriptor:

- a type declaration uses `type`;
- a field, property, enum case, or annotation member uses `term`;
- a method, function, getter, setter, operator, or constructor uses `callable`.

The callable disambiguator is the UTF-8 JSON Canonicalization Scheme (JCS)
serialization of the profile's callable-signature identity object, embedded as
the core descriptor's string value. Parameter types, receiver type, parameter
mode, nullability, and generic arity participate exactly as defined for that
language. For Java, adapted formal parameter types and type parameters
participate, a varargs parameter is normalized to its array type, and receiver
parameters do not participate. Return type,
throws clauses, annotations, default values, and use-site type arguments are not
source callable identity in this version and therefore are not serialized in
the identity payload. The normalized constructor name is `<constructor>` and
cannot collide with a method or factory. Java overloads retain resolver-visible
source parameter types: boxing is not identity equivalence, while varargs and
the corresponding array type normalize to the same Java signature.
Kotlin extension receivers and Scala by-name/repeated parameters remain
explicit. A source identity does not change merely because erasure, compiler
lowering, or a bridge creates a related JVM member.

`canonicalName` is a resolver-derived type identity, not source text. It MUST
use the selected language's fully qualified declaration identity after alias
expansion and MUST encode type parameters by owner-relative position. A
producer that cannot construct the same canonical type identity independently
MUST report the affected source identity as unavailable or incomplete; it MUST
NOT substitute a pretty-printed type, imported short name, or JVM descriptor.

Generated or synthetic source declarations need a scheme-defined stable
generation key. A producer unable to construct one MUST omit the target and
report partial or unknown declaration coverage with an appropriate limitation;
it MUST NOT use a source location, occurrence ordinal, or generated display name
as portable identity. Named member and nested types follow the normal owner
path. Local, anonymous, and lambda entities are not portable in this version
unless the front end proves an owner-relative stable key; otherwise they are
omitted from portable source coverage.

## JVM binary identity

`csmi.jvm-binary-identity` identifies an exact class-file entity. Its comparison
tuple is the exact profile version, optional JDK module, owner JVM internal
name, binary entity, and selected class-file variant. Generic signatures,
class-file flags, and relocation evidence are identity-bound metadata: they are
compared as facts but do not merge or split an otherwise exact binary key.

Class members use JVM field or method descriptors exactly as stored in the
class file. Constructors use the bytecode name `<init>`; class initializers use
`<clinit>`. Return type is part of a method descriptor. A generic `Signature`
attribute is preserved separately and MUST NOT replace or rewrite the erased JVM
descriptor. Bridge, synthetic, mandated, and generated flags are explicit facts;
they neither merge the member with its target nor make it ignorable.

A default interface method is an ordinary binary method owned by its interface,
with its exact name and descriptor. A compiler bridge is a different binary
method even when mapping evidence relates it to the same source declaration.
Named inner and nested classes use their class-file internal names. Local,
anonymous, lambda, and other compiler-generated classes have portable binary
identity only within exact artifact and selected-variant scope; source/binary
mapping remains indeterminate unless authoritative compiler evidence supplies
the relation.

For a normal JAR entry, `variant.release` is `0` and `entryPath` is the base
class path. For a multi-release JAR entry, release is at least 9 and the path is
under the matching `META-INF/versions/N/` tree. Before comparing or applying a
binary identity, a consumer MUST select the entry using the JAR's multi-release
status and the effective Java release. Unavailable manifest, runtime-release,
or entry evidence makes variant selection indeterminate. It MUST NOT silently
select the base entry.

JDK classes additionally name their JDK module. Maven, Gradle, and JAR identity
remain in the enclosing artifact selector rather than the symbol key. Exact
Maven artifacts use canonical Maven PURLs, including classifier/type qualifiers
when they distinguish artifacts. Version ranges use the Maven VERS procedure.
Resolved Gradle variants use the identity of their selected artifact bytes;
Gradle component or variant display strings are not PURLs. When no registered
PURL mapping establishes the selected artifact, the producer MUST use an
exact-digest-scoped artifact identity supplied by a required vocabulary or
report applicability as indeterminate. JDK images likewise use an applicable
canonical PURL type or exact-digest-scoped identity. A consumer lacking
evidence for a required qualifier reports indeterminate applicability.

Shading changes binary identity. A relocated member names its post-relocation
owner as `owner`, records the original owner, the relocation rule, and a digest
of authoritative relocation evidence. Equal-looking bytecode or a prefix
resemblance is insufficient. When relocation evidence is unavailable, the
mapping is indeterminate rather than direct.

The selector for relocated bytes identifies the produced shaded artifact, not
the upstream dependency whose bytes were incorporated. An upstream PURL or
matching unrelocated owner is not an alternative selector for the shaded JAR
unless trusted artifact-equivalence evidence independently proves that claim.

## Source-to-binary mappings

`csmi.java-jvm-mapping` defines the namespaced fact family
`java-jvm-mapping`. Its scope is one exact source symbol within the enclosing
artifact identity. An `established` fact contains one or more exact binary
symbol IDs, a mapping kind, and authoritative evidence. Fact equality requires
equal source, target set, mapping kind, and evidence set. Different established
target sets for the same exact scope conflict unless a producer demonstrates
that they describe distinct selected artifact variants.

Mapping kinds have these meanings:

- `direct`: one source declaration emits the named binary member without
  erasure-changing or language-specific lowering;
- `erased`: the JVM descriptor is an erasure of the source declaration;
- `bridge`: the target is a compiler bridge related to the declaration;
- `lowered`: language lowering creates one or more binary members, including
  Kotlin default-argument helpers or Scala encodings;
- `generated`: processing, macros, or compiler synthesis creates the target;
- `relocated`: verified shading or bytecode rewriting changes binary identity.

The source symbol and every binary symbol MUST resolve under their respective
exact schemes and applicable artifact scopes. Mapping evidence MUST be tied to
the exact selected build or class-file bytes. One-to-many lowering is explicit;
consumers MUST NOT choose a preferred target by name.

An `indeterminate` payload is a typed record that the producer cannot establish
or contradict a mapping with available evidence. It contains no binary target.
An `unsupported` payload records the exact unimplemented vocabulary and version.
Neither state asserts a negative mapping, contributes an established relation,
nor licenses identity equivalence.

The family coverage scope is `{ "sourceSymbol": <exact-local-symbol-id> }` in
the enclosing artifact identity, exact profile version, and exact selected
variant. `complete` licenses only the inference that every established mapping
for that source and variant has been emitted. It does not assert that source and
binary identities are equal, that the declaration emitted no bytecode, or that
another source language has no mapping. Indeterminate or unsupported mapping
evidence prohibits `complete` for that scope.

## Compatibility constraints

`csmi.jvm-compatibility` values are conjunctive and are evaluated only after
artifact applicability is matched. `javaRelease` and `classFileMajor` are
inclusive ranges; a minimum greater than a maximum is semantically invalid.
`multiReleaseSelection` is the effective Java release used to select a JAR
variant. Kotlin metadata and Scala binary versions constrain interpretation of
language-specific metadata, not JVM member identity. Compiler flags belong here
only when a separately versioned vocabulary defines deterministic values; this
version intentionally has no free-form flags field.

`jvmVendor` is an absolute URI controlled by or canonically assigned to the
vendor and is compared by exact URI identity. A product display name, runtime
banner, or case-folded organization string is not a vendor identifier.

Contradicted evidence yields `incompatible`. Missing release, bytecode, module,
vendor, language-metadata, platform, or multi-release evidence yields
`indeterminate`. An unsupported required compatibility vocabulary makes the
affected model uninterpretable. All three fail closed by default and none
changes the independently reported artifact-applicability outcome.

## Fixture taxonomy

Files under `fixtures/profiles/java-jvm/valid/` are structurally valid payloads.
They cover Java overloads, constructors, Kotlin and Scala lowering, bridges,
synthetic/generated declarations, erasure and generic signatures,
multi-release variants, shading, typed unsupported mapping, and indeterminate
evidence. Files under `invalid/` are structurally rejected near misses, such as
an unsupported schema version, a constructor spelled as a source method, a JVM
method without a descriptor, a multi-release entry represented as a base
variant, or an established mapping without evidence.

Files under `semantic-invalid/` intentionally pass the profile schema but
violate normative invariants, including reversed compatibility ranges, a Java
varargs signature that was not normalized to its array type, and a
multi-release entry whose path version disagrees with its selected release.

Additional semantic near misses that JSON Schema alone cannot reject are:

| Case | Outcome |
| --- | --- |
| Same Java display name but `String` versus `byte[]` source parameter | different |
| Constructor versus same-parameter static factory | different |
| Same erased JVM descriptor but distinct source declarations | different source identities; mapping required |
| Bridge versus bridged implementation | different binary identities; mapping may relate them |
| Base class entry versus selected multi-release entry | different binary variant |
| Unverified original versus shaded owner | indeterminate mapping |
| Required profile version `0.2` at a `0.1`-only consumer | unsupported and uninterpretable |
| Missing candidate Java release for a release constraint | indeterminate compatibility |
