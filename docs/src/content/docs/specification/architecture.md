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

## A small portable algebra

Language neutrality does not require CSMI to standardize the union of all
language features. Doing so would turn the interchange into a universal
compiler IR and require every consumer to understand distinctions irrelevant to
its analysis.

Instead, CSMI standardizes a small algebra of portable observations. Language
and ecosystem profiles supply the evidence that maps real declarations and
behavior into that algebra, while semantic profiles add reusable analysis
domains without enlarging the core.

| Layer | Responsibility | Examples |
| --- | --- | --- |
| Core | Stable identities, boundaries, facts, and claim mechanics shared by independent analyzers. | Artifact and symbol identity envelopes, callable boundary locations, conservative may-information transfer, provenance, and completeness. |
| Semantic profiles | Analyzer-neutral observations designed for reuse across multiple languages but not required by every consumer. | Value transfer, mutation, allocation, escape, invocation, ownership, and taint. |
| Language and ecosystem profiles | Exact evidence for mapping source or binary constructs into core and semantic-profile facts. | Import and overload resolution, compiler configuration, ABI descriptors, package bindings, and generated-code provenance. |

Language profiles are therefore primarily evidence-bearing mappings. They may
define exact identities and language semantics needed to justify a fact, but
they should not make their source language the canonical shape of a supposedly
portable concept. Supporting CSMI core does not require supporting every
language or every profile.

## Conservative projection

A producer may project a rich language fact into a weaker portable fact when
the projection is sound and the lost information is explicit. For example, a
guarded language-specific flow may be represented as an unguarded core
may-information transfer. A complex type may remain `unknown`. Several precise
declaration kinds may map to the same coarse core category.

The governing rule is:

> Erasure may reduce precision, but must not strengthen identity,
> applicability, semantic truth, coverage, or completeness.

Consequently, an unresolved declaration cannot become an approximately named
symbol, two similarly named operations cannot become the same identity, and an
incomplete language analysis cannot produce a complete portable claim. When no
sound projection exists, the producer preserves typed uncertainty or reports
the semantics as unsupported rather than inventing an approximation.

Exact language facts may remain alongside their weaker portable projection for
consumers that implement the corresponding profile. A consumer may ignore that
additional evidence only when its vocabulary use is optional and independent;
required evidence remains necessary to interpret every affected fact.

## Growing the vocabulary

A concept is a candidate for core only when independent implementations can
give it stable language-neutral meaning and it is broadly necessary to
interpret other portable facts. Repeated use alone is insufficient: equality,
conflict, merge, and completeness must also be language independent.

Concepts should normally begin in a language profile or vendor extension. When
materially different languages independently demonstrate the same semantic
algebra, their common observation may be extracted into a shared standard
profile. Promotion into core should remain rarer because every core addition
increases the minimum obligation for all conforming consumers.

## Normative artifacts

- [CSMI v0.1 specification source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/spec/0.1/specification.md)
- [Read the rendered v0.1 specification](../v0-1/)
- [CSMI v0.1 JSON Schema](/schema/0.1/schema.json)
- [Conformance fixtures](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures)

This page is a concise navigational rendering. Where it differs from the
versioned repository specification, the repository source is authoritative.
