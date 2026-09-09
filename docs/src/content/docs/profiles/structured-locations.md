---
title: Structured summary locations
description: Bounded analyzer-neutral fields, keyed and indexed cells, variant payloads, and widened tails for procedure summaries.
---

<span class="csmi-label csmi-label--normative">Normative profile</span>

`csmi.structured-locations` version `0.1.0` supplies the standard projection
scheme for bounded procedure-summary sublocations. It supports resolver-proven
fields and variants, key and index selectors tied to stable invocation slots,
constant indices, terminal wildcards, and explicitly widened tails.

The profile preserves the core distinction between conservative precision and
coverage. It does not define receiver resolution, source lowering, ownership,
or implicit cleanup, and unsupported projections fail closed rather than being
flattened to their roots.

- [Read the normative profile source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/structured-locations/0.1/profile.md)
- [Open the profile payload schema](/schema/profiles/structured-locations/0.1/schema.json)
- [Review the conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/structured-locations.md)
