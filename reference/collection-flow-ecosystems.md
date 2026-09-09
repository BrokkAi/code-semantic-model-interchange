# Collection-flow ecosystem mappings

This is API evidence for the analyzer-neutral concepts in
[collection-flow 0.1.0](../profiles/collection-flow/0.1/profile.md), checked on
2026-09-09. These are proposed semantic mappings, not claims of implemented
compiler adapters. [Conformance](../conformance/collection-flow.md) separates
executable reference evidence from production interoperability.

| Ecosystem | Portable mapping | Near miss |
| --- | --- | --- |
| Scala collections | An instantiated keyed receiver preserves ordered K/V type arguments; update transfers its value argument to an entry value; an entry callback can receive a product. | Same-named custom `update` or `foreach` is not the standard operation. Resolved callback arity must account for compiler adaptation. |
| Java collections | `Map.forEach` delivers key and value to two BiConsumer arguments; `entrySet` iteration delivers an entry whose getters expose key/value separately. | Do not turn the two BiConsumer parameters into one tuple or treat every Map.Entry as a positional product. |
| Kotlin collections | The Map extension `forEach` supplies an entry; resolved component operations expose key/value to destructured bindings. | JVM member/extension overload selection must be resolved; a user-defined component method need not preserve the entry's key or value. |
| C# collections | KeyValuePair deconstruction exposes ordered key/value outputs after the exact deconstructor has been selected. | The `foreach` statement itself is not a higher-order callback API; custom Deconstruct overloads do not inherit KeyValuePair semantics. |

Scala's documented mutable Map operations establish the key/value update and
entry iteration cases. Product lowering must use the resolved language-level
shape, including any compiler adaptation, rather than the documentation's
rendered signature. [Scala MapOps](https://www.scala-lang.org/api/2.x/scala/collection/mutable/MapOps.html)

Java's API distinguishes `forEach(BiConsumer)` from the entry set and documents
the two consumer arguments. This is direct evidence that the portable callback
boundary must preserve parameter count rather than hard-code an entry tuple.
[Java 24 Map](https://docs.oracle.com/en/java/javase/24/docs/api/java.base/java/util/Map.html)

Kotlin's Map extension supplies an entry to its action. Its entry component
operations provide explicit semantic evidence for destructuring; the compiler's
resolved operation remains necessary at a particular use site.
[Kotlin MutableMap](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-mutable-map/),
[Kotlin Map.Entry](https://kotlinlang.org/api/core/kotlin-stdlib/kotlin.collections/-map/-entry/)

The .NET KeyValuePair deconstructor exposes key and value in that order. This
supports the same ordered component observation without claiming that C#
iteration is callback invocation or that all deconstructable objects are pairs.
[KeyValuePair.Deconstruct](https://learn.microsoft.com/en-us/dotnet/api/system.collections.generic.keyvaluepair-2.deconstruct?view=net-10.0)

## Information boundary

Retained: exact artifact and declaration identity, ordered structured generic
arguments, abstract key/value selection, callback parameter positions, and
explicit component positions with provenance and independent coverage.

Conservatively erased: collection implementation, storage layout, iteration
order, allocation strategy, and compiler-local binding identifiers. A
may-information transfer does not assert value preservation, aliasing,
atomicity, insertion success, non-emptiness, or absence of exceptions.

Unsupported without additional exact evidence: inheritance/type-variance
substitution, raw or existential receiver arguments, custom equality semantics
needed for disjointness, arbitrary extractors/deconstructors, and unresolved
callback adaptation. These remain typed gaps rather than guessed portable
facts. No language's display name, signature text, or source pattern is identity.
