---
title: Portable runtime contracts 0.2
description: Reviewed runtime behavior, target-scoped applicability, and exact executable runtime-value evidence.
---

`csmi.runtime-values` **0.2.0** lets a reviewed runtime API contract apply over
an explicit compatible version range. Its contract digest identifies semantic
content. Artifact-specific contracts retain an additional requirement for
actual artifact bytes and their digests.

The profile separates the contract from evidence about the analyzed target and
from analyzer-generated occurrence bindings and executable observations.
Declared target analysis remains conditional on that target; it does not verify
the deployed runtime. Mixed Node/browser projects retain separate source
partitions, and unknown or unsupported targets remain visible.

Node environment and argument examples cover arbitrary static keys, launch
origins, mutation and deletion, own-value lookup, worker copies and shared
storage, and uncertain key equality. Python environment mappings demonstrate
the same contract boundaries with different missing-key and initialization
semantics. Complete lookup/effect proof remains separate from activation.

This version has no implicit precedence between portable and artifact-specific
contracts. Conflicting applicable models prevent activation. Review and trust
are scoped to exact content and target under a consumer policy.

- [Normative profile](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/runtime-values/0.2/profile.md)
- [Payload schema](/schema/profiles/runtime-values/0.2/schema.json)
- [Conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/runtime-values-0.2.md)
- [Bifrost consumer migration](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/reference/bifrost-runtime-contract-migration.md)
- [Existing runtime-values 0.1.0](/profiles/runtime-values/)

Core CSMI remains version 0.1. Existing 0.1.0 runtime documents are unchanged;
a consumer must explicitly support 0.2.0 before interpreting these facts.
Repository conformance establishes interchange behavior, not production
consumer adoption or verification of a deployed runtime.
