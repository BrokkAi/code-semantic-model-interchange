---
title: Examples and fixtures
description: Explanatory examples and structural or semantic conformance fixtures.
---

<span class="csmi-label">Explanatory and conformance material</span>

Complete representative documents live under [`fixtures/valid/`](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures/valid).
Structurally invalid documents live under [`fixtures/invalid/`](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures/invalid).

The separate [`fixtures/semantic-invalid/`](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures/semantic-invalid)
set intentionally passes JSON Schema while violating a named semantic
invariant. This preserves the boundary between parsing a document and proving
that its claims are conforming.

## Python profile

The normative [`csmi.python` 0.1 profile](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/python/0.1/profile.md)
has a separately versioned [payload schema](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/python/0.1/schema.json),
focused payload fixtures, and [semantic conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/python-profile.md).
It deliberately keeps PyPI distribution identity, import-module identity,
runtime declarations, and stub evidence distinct.

## JavaScript, TypeScript, and Node profiles

Repository-owned standard-profile payloads are validated separately. The
focused valid and invalid payloads live beside each schema under
[`profiles/`](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/profiles).
The representative
[`javascript-typescript-node.json`](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/fixtures/valid/javascript-typescript-node.json)
fixture exercises Node builtin aliases, separate `@types/node` identity,
CommonJS/ESM binding evidence, a conditional npm export, TypeScript/TSX
compatibility, scoped completeness, and fail-closed profile uses.

## Value-transfer and C/C++ profiles

The [`csmi.value-transfer` profile](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/value-transfer/0.1/profile.md)
attaches identity-separating copy, move, conversion, boxing, or unboxing meaning
to an existing core transfer and separately describes exact type-value and
implicit-operation facts. Its fixtures distinguish copies from reference and
pointer aliases and preserve unknown operation or invalidation outcomes.

The [C and C++ profile family](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/cpp/0.1/profile.md)
uses `csmi.c-cpp-resolution` for exact artifact and resolver context and
`csmi.cpp` for a structured canonical
`std::string` alias target, and reproducible declaration keys for the selected
copy constructor and copy assignment. Same-named custom types and incomplete
header closure remain non-matches.
