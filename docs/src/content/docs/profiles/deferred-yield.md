---
title: Deferred-yield profile 0.1
description: Linked factory and resume contracts for handles that retain a source and yield items later.
---

`csmi.deferred-yield` version `0.1.0` links an exact callable that constructs a
handle, its exact handle type, and an exact callable that later resumes it. A
handle retains a collection source with borrowed-shared, borrowed-exclusive,
or owned retention. Each resume
yields zero or one item; a handle may support zero or more resumes. Item key
and value mapping, delivery, validity, and invalidation are explicit.

The profile is analyzer-neutral and independently versioned. Rust iteration is
motivating evidence, not a Rust-specific contract. Unsupported required
semantics remain uninterpretable, and partial or unknown coverage cannot become
an empty complete summary.

- [Normative profile](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/deferred-yield/0.1/profile.md)
- [Payload schema](/schema/profiles/deferred-yield/0.1/schema.json)
- [Conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/deferred-yield.md)
- [Consumer integration](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/reference/deferred-yield-lowering.md)
