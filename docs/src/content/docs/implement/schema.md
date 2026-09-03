---
title: JSON Schema
description: The normative JSON serialization schema for CSMI v0.1.
---

<span class="csmi-label csmi-label--normative">Normative</span>

The canonical schema identifier for the v0.1 JSON serialization is:

```text
https://csmi.brokk.ai/schema/0.1/schema.json
```

Validation must not depend on network retrieval. Consumers should package or
pin the repository copy associated with the semantic-model version they
support.

- [Open the canonical schema](/schema/0.1/schema.json)
- [View schema source on GitHub](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/spec/0.1/schema.json)
- [Read structural and semantic conformance](/specification/v0-1/#4-conformance)

Versioned standard profiles publish separate schemas for their delegated
payloads. Core validation does not imply profile support:

- [JavaScript and TypeScript profile 0.1](/schema/profiles/javascript-typescript/0.1/schema.json)
- [Node compatibility profile 0.1](/schema/profiles/node-compatibility/0.1/schema.json)
- [Java/JVM profile family](/profiles/jvm/)
- [Value-transfer profile 0.1](/schema/profiles/value-transfer/0.1/schema.json)
- [C and C++ profile 0.1](/schema/profiles/cpp/0.1/schema.json)

Validate repository profile fixtures with
`python3 scripts/validate-profiles.py`, with the profile-specific semantic
checks in `scripts/validate-value-transfer.py` and
`scripts/validate-cpp-profile.py`.
