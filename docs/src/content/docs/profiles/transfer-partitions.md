---
title: Transfer partition coverage
description: Independently complete normal-result transfer partitions without closing a callable.
---

<span class="csmi-label csmi-label--normative">Normative profile</span>

`csmi.transfer-partitions` version `0.1.0` lets a producer mark the core
input-to-one-normal-result transfer partition complete while leaving other
outputs and the callable-wide core summary partial or unknown. An empty
partition closes only that exact input/result transfer set. It says nothing
about exceptions, caller-visible state, callbacks, mutation, or purity.

- [Read the normative profile and contract crosswalk](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/transfer-partitions/0.1/profile.md)
- [Open the profile scope schema](/schema/profiles/transfer-partitions/0.1/schema.json)
- [Review conformance and Python/JavaScript examples](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/transfer-partitions.md)
