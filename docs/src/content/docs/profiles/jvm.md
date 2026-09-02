---
title: Java and JVM profiles
description: Resolver source identity, JVM class-file identity, evidence-bearing mapping, and compatibility for Java, Kotlin, and Scala.
---

<span class="csmi-label">Profile summary</span>

The Java/JVM profile family separates what a Java, Kotlin, or Scala resolver
declares from what a JVM class file exposes. Source and JVM-binary symbols are
different CSMI symbols even when their rendered names resemble one another. A
separate mapping vocabulary records an evidence-backed projection between them;
it does not merge their identities.

The normative definition is
[`profiles/java-jvm/0.1/profile.md`](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/java-jvm/0.1/profile.md).
Its four capabilities are independent, exact-version vocabulary uses:

| Identifier | Version | Purpose |
| --- | --- | --- |
| `csmi.java-source-identity` | `0.1` | Java, Kotlin, or Scala resolver-proven source identity. |
| `csmi.jvm-binary-identity` | `0.1` | Verified JVM class-file member identity and selected variant. |
| `csmi.java-jvm-mapping` | `0.1` | Evidence-bearing source-to-binary projection. |
| `csmi.jvm-compatibility` | `0.1` | Runtime, class-file, language-metadata, and variant constraints. |

Each use must declare its schema, exact `0.1` version, requiredness, and
affected units. Supporting one capability does not imply support for another.
Ignoring an optional payload is allowed only within the boundary the producer
declares. Anything whose meaning depends on a capability requires it.

## Source declarations

`csmi.java-source-identity` compares the exact profile version, source
language, package segments, owner path, declaration variant, and its
language-specific signature components. `origin` and generation kind are
metadata; a stable generation key participates only when the resolver-visible
tuple would otherwise collide. Strings compare by exact Unicode scalar sequence
after language escape processing; no case folding, silent normalization, or FQN
joining is performed.

The core descriptor path maps package segments to `namespace`, owners to
`type`, and the terminal declaration to the appropriate core descriptor. A
callable's disambiguator is the JCS serialization of the profile signature.
Return types never participate. Java follows its resolver signature rules,
including normalization of varargs to the corresponding array type; primitive
and boxed parameters remain distinct.
Kotlin extension receivers and Scala by-name or repeated parameters remain
explicit.

Constructors use `<constructor>`, which cannot collide with a method or static
factory. Generated and synthetic source declarations require the profile's
stable generation key. If a producer cannot construct one, it must omit the
target and report partial or unknown declaration coverage instead of inventing
an ID from a source location or generated display name.

Source identity is unchanged when erasure, compiler lowering, or a bridge
creates a related JVM member. A generic source declaration and a use-site
reference to it remain one declaration identity.

## JVM binary entities

`csmi.jvm-binary-identity` compares the exact profile version, optional JDK
module, post-relocation owner internal name, exact binary entity, and selected
class-file variant. Generic signatures, flags, and relocation evidence are
identity-bound facts rather than extra linkage components. Members use the JVM
field or method descriptor stored in the class
file; methods include their return type and void result. Constructors use
`<init>` and initializers use `<clinit>`.

The optional `Signature` attribute is mapping and generic-shape evidence. It is
preserved separately and never replaces the dispatching JVM descriptor. Bridge,
synthetic, mandated, and generated flags are structured facts: they do not merge
a bridge with its target or make a member disappear from binary identity.

For a normal JAR entry, `variant.release` is `0` and the entry path is the base
class path. A multi-release entry has release 9 or greater and a matching path
under `META-INF/versions/N/`. Consumers must select an entry from the JAR's
multi-release status and effective Java release before comparing or applying a
binary identity. Missing manifest, runtime-release, or entry evidence makes
variant selection indeterminate; the base entry is not a default witness.

JDK classes name their JDK module. Maven, Gradle, and JAR identity remain in
the enclosing artifact selector. Exact Maven artifacts use canonical Maven
PURLs, including type and classifier qualifiers that distinguish artifacts;
version ranges use Maven VERS. Gradle display coordinates are not artifact
identity: the selected bytes need a registered PURL mapping or exact digest
scope. JDK images likewise require an applicable canonical PURL or exact digest
scope.

Shading changes binary identity. A relocated member identifies its
post-relocation owner plus its original owner, relocation rule, and a digest of
authoritative relocation evidence. Similar bytecode or a namespace-prefix match
is not proof. Without relocation evidence, a shaded mapping is indeterminate.

## Evidence-bearing mapping

`csmi.java-jvm-mapping` scopes one established, indeterminate, or unsupported
result to one exact source symbol, exact profile version, and selected binary
variant. An established result names one or more exact binary symbol IDs, one
mapping kind, and at least one authoritative evidence record. The kinds are
`direct`, `erased`, `bridge`, `lowered`, `generated`, and `relocated`.

Every endpoint must resolve under its respective scheme and artifact scope.
Mapping evidence must be tied to the selected build or class-file bytes. A
source declaration may map one-to-many for bridges, Kotlin default-argument
helpers, Scala encodings, or other lowering. Consumers preserve the full target
set; they do not choose a favorite by name or descriptor similarity.

`indeterminate` is a typed no-target result such as missing class-file bytes,
missing compiler metadata, ambiguous lowering, unselected artifact variant, or
unverified relocation. `unsupported` names the exact vocabulary and version
that cannot be interpreted. Neither state is a negative mapping, identity
equality, or permission to discard either side.

`complete` mapping coverage licenses only the inference that every established
mapping for that exact source symbol and selected variant has been emitted. It
does not close Java source declarations, JVM binary declarations, mappings for
another language, or mappings for another variant. Indeterminate or unsupported
evidence prohibits a complete mapping claim.

## Compatibility and completeness

`csmi.jvm-compatibility` is conjunctive and runs only after artifact
applicability is `matched`. It supports inclusive `javaRelease` and
`classFileMajor` ranges, `targetPlatform`, `jdkModule`, `jvmVendor`,
Kotlin metadata version, Scala binary version, and effective
`multiReleaseSelection`. A minimum above a maximum is semantically invalid.
Language metadata constrains interpretation of language-specific metadata; it
does not rewrite JVM member identity. JVM vendors use exact absolute URIs, not
runtime-banner or organization display strings.

Contradiction is `incompatible`. Missing comparable evidence is
`indeterminate`. An unsupported required compatibility use is uninterpretable.
All three fail closed and none changes the independently evaluated artifact
applicability outcome.

Completeness remains family-scoped. Parsing a subset of source files or class
files, skipping non-public members, failing class verification, or failing to
select a multi-release entry is at most partial coverage with a typed
limitation. A complete source set does not close binary coverage, and a
complete binary set does not close source or mapping coverage. Unsupported
required identities, mappings, compatibility constraints, or intrinsic type
semantics fail closed for their affected boundary; unrelated facts with provably
independent boundaries remain usable.
