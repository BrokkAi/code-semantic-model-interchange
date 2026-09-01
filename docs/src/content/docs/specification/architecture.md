---
title: Specification architecture
description: The normative layers and conformance model of CSMI v0.1.
---

<span class="csmi-label csmi-label--normative">Normative source</span>

CSMI separates semantic meaning from machine representation. The v0.1 model is
defined in the repository's [normative specification](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/spec/0.1/specification.md),
with JSON as its first normative serialization.

| Layer | Role |
| --- | --- |
| Semantic model | Analyzer-neutral concepts and conformance obligations. |
| Serialization | A concrete encoding of the semantic model. |
| Structural schema | JSON Schema constraints on document shape. |
| Semantic conformance | Obligations structural validation cannot express. |
| Pack | Distribution, licensing, provenance, and integrity envelope. |
| Transport and registry | Out of scope for v0.1. |

JSON Schema validates structure. It does not prove that references resolve,
that artifact applicability holds, that a summary port exists in its callable
shape, or that a completeness claim is justified.

## Normative artifacts

- [CSMI v0.1 specification source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/spec/0.1/specification.md)
- [Read the rendered v0.1 specification](../v0-1/)
- [CSMI v0.1 JSON Schema](/schema/0.1/schema.json)
- [Conformance fixtures](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures)

This page is a concise navigational rendering. Where it differs from the
versioned repository specification, the repository source is authoritative.
