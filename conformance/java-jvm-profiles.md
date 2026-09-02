# Java/JVM profile conformance cases

These cases are normative for the exact Java/JVM profile version `0.1`.
Profile JSON Schema checks payload shape; this document defines the additional
semantic outcomes that structural validation cannot prove. Focused
semantic-invalid fixtures are executed by `scripts/validate-profiles.py`.

## Source identity

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Independently resolved Java `normalize(String)` declarations with equal artifact scope and canonical JCS signature | `same` | Resolver-proven source components agree. |
| Java `normalize(String)` versus `normalize(byte[])` | `different` | Formal parameter identity differs. |
| Java `normalize(int)` versus `normalize(Integer)` | `different` | Boxing is not declaration identity. |
| Java `join(String...)` versus `join(String[])` | `same` | Java varargs normalizes to the array formal parameter type. |
| Constructor versus equal-parameter static factory | `different` | `<constructor>` and the method name are distinct. |
| Equal display text derived from different imports | `indeterminate` until resolved | Display text is not a canonical type identity. |
| Named declaration with different `origin` metadata | `same` | Origin does not override resolver identity. |
| Local or anonymous source entity identified only by offset or ordinal | Semantically invalid portable key | This profile defines no portable source-order identity. |

## Binary identity and selected variants

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Equal JDK module, owner internal name, member name, descriptor, artifact scope, and selected variant | `same` | Every binary linkage component agrees. |
| Method descriptors differing only in result descriptor | `different` | JVM method descriptors include the result. |
| Generic `Signature` differs but name and descriptor agree | Same binary key; conflicting metadata fact if scopes are equal | Generic signatures do not replace linkage identity. |
| Bridge and bridged method with different descriptors | `different` | Bridge metadata never merges members. |
| Default interface method and equal-named class method | `different` | Their binary owners differ. |
| Base entry versus selected release-17 entry | `different` variant | Multi-release selection is part of scope. |
| `release: 17` with an entry under `META-INF/versions/11/` | Semantically invalid | The selected release and entry path disagree. |
| Local class under exact JAR digest and exact internal name | Artifact-local binary identity | The bytes establish scope; no source mapping follows. |

## Mapping and interoperation

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Java declaration plus compiler/class-file evidence names one exact method | `mapped` | Exact evidence establishes the projection without merging keys. |
| Kotlin default-argument declaration maps to primary and `$default` methods | `mapped-one-to-many` | Lowering targets remain explicit. |
| Scala declaration maps to an erased method plus a compiler bridge | `mapped-one-to-many` | Erasure and bridge relations are evidence-bearing. |
| Bridge flag or descriptor resemblance without compiler evidence | `indeterminate` | Resemblance does not prove a source peer. |
| Generated JVM member has no source declaration | `binary-only` | Generation is not evidence of a source identity. |
| Same producer-local ID on source and binary records | `indeterminate` | Local handles are not cross-scheme identity. |
| Required mapping version is unsupported | `uninterpretable` for its affected boundary | Consumers must fail closed. |

Source and binary identities are always `different` under core identity
comparison because their schemes differ. `mapped` is a relation result, never
`same`.

## Artifact applicability and compatibility

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Canonical Maven PURL including distinguishing classifier/type plus matching JAR digest | `matched` | Every selector constraint agrees. |
| Required classifier is absent from candidate evidence | `indeterminate` | Missing evidence is not a mismatch. |
| Gradle display coordinate without registered PURL mapping or exact selected bytes | `indeterminate` | Display coordinates do not identify the resolved variant. |
| Exact JDK image digest, module evidence, and compatible release | `matched` and `compatible` | Artifact and compatibility are independently established. |
| Multi-release JAR with unknown manifest or effective release | `indeterminate` variant selection | The base entry is not guessed. |
| Original upstream PURL offered for relocated bytes in a shaded JAR | `not matched` | The produced shaded artifact has a different identity. |
| Shaded artifact matches, but relocation evidence is missing | Artifact `matched`; mapping `indeterminate` | Applicability does not prove relocation. |
| Compatibility minimum exceeds maximum | Semantically invalid | The conjunctive range is impossible. |
| Required JVM compatibility profile is unsupported | Model boundary `uninterpretable` | Schema resemblance cannot replace profile support. |

## Requiredness and completeness

An identity or compatibility use is `required` whenever it affects binding or
applicability. A mapping use is required for any fact, aggregation, or negative
inference that depends on the projection. A purely descriptive origin
attachment may be optional only if removing it leaves all supported results and
coverage unchanged.

Completeness is scoped by exact artifact selector and selected variant,
identity scheme and exact version, fact family, and family scope. Complete JVM
declaration coverage does not close Java/Kotlin/Scala source declarations or
mapping relations. An indeterminate mapping, unselected multi-release variant,
unsupported required profile, unresolved generated declaration, or skipped
class file prohibits a complete claim for the affected scope.

## Non-normative Bifrost reference mapping

This table demonstrates a possible adapter boundary; Bifrost names are not
CSMI identity and are never normative.

| Bifrost-side evidence | CSMI profile projection |
| --- | --- |
| Resolver-proven Java/Kotlin/Scala declaration plus canonical owner/type information | Construct `csmi.java-source-identity` components. |
| Parsed class owner, member name, descriptor, flags, `Signature`, module, and selected JAR entry | Construct `csmi.jvm-binary-identity` components. |
| Compiler symbol table, Kotlin/Scala metadata, or verified source-to-class build trace | Emit `csmi.java-jvm-mapping` with exact endpoint symbols and evidence digest. |
| Maven/JAR digest, Java release, class-file major, module, and metadata versions | Evaluate core artifact selectors, then `csmi.jvm-compatibility`. |
| Bifrost database ID, rendered FQN, regex match, or source-text resemblance | No portable projection; report indeterminate or omit with scoped incompleteness. |

An independent consumer can implement these published construction and outcome
rules from profile artifacts alone; it need not parse Bifrost's authored pack
schema or use a Bifrost side channel.
