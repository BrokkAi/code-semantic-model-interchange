---
title: Status and versioning
description: The experimental status and version layers of CSMI v0.1.
---

CSMI v0.1 is an **experimental draft**. It is not yet a stable standard, and
interoperability has not yet been demonstrated by independent producer and
consumer implementations.

The project versions semantic meaning, serialization, schema identity, and
extension vocabularies independently. A consumer must not infer semantic
compatibility from a schema validator accepting JSON alone.

The repository remains the source of truth. Published documentation renders
version-controlled content and links to its exact schema and source revision.

Separately versioned standard vocabularies define language identity,
applicability, and analyzer-neutral semantic extensions without changing the
language-neutral core. The `csmi.value-transfer`, `csmi.structured-locations`,
`csmi.c-cpp-resolution`, and `csmi.cpp` profiles are version `0.1.0` while the containing documents remain
CSMI semantic model `0.1` serialized as `0.1-json`. Profile evolution follows
its own exact version and schema URI; schema acceptance alone is not support.

The `csmi.collection-flow` profile begins at exact version `0.1.0`. This is a
new vocabulary, not an expansion of the accepted core type or transfer forms.
Existing consumers remain compatible with old documents; consumers receiving
this required profile must implement it or preserve uninterpretable affected
units. Repository conformance evidence does not certify production adapters.

The independent `csmi.deferred-yield` profile also begins at exact version
`0.1.0`. It does not revise collection-flow `0.1.0`: producers opt in only for
exact factory/resume/handle-type scopes, and consumers that lack this required vocabulary
must keep those scopes uninterpretable rather than treating omitted yields as
an empty stream.
