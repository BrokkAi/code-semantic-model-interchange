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
