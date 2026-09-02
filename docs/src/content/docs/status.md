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

The first separately versioned standard language vocabulary is
[`csmi.python` 0.1](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/python/0.1/profile.md).
It defines Python identity and applicability without making the language-neutral
core depend on Python packaging or import semantics.
