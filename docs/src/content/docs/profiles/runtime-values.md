---
title: Runtime exposure and keyed-read values
description: Analyzer-neutral runtime-global activation and operation-specific keyed-read value evidence.
---

<span class="csmi-label csmi-label--normative">Normative profile</span>

`csmi.runtime-values` version `0.1.0` separates producer-authored runtime exposure and read-behavior contracts from per-access binding and load observations. Static map properties and array indices remain value-access identities, never fabricated declarations.

The profile keeps activation, lexical shadowing, rebinding, mutation, exceptional behavior, materialization, provenance, completeness, and consumer support explicit. Unsupported semantics cannot silently become an empty or exact model.

- [Read the normative profile source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/runtime-values/0.1/profile.md)
- [Open the profile payload schema](/schema/profiles/runtime-values/0.1/schema.json)
- [Review the conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/runtime-values.md)
