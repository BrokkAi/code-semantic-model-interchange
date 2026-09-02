---
title: Rust profile 0.1
description: Deterministic Rust source identity, Cargo applicability, compilation compatibility, and native mappings for CSMI.
---

<span class="csmi-label csmi-label--normative">Normative profile</span>

`csmi.rust` version `0.1.0` defines resolver-proven Rust source-item identity
while keeping Cargo packages, target crates, workspace resolution, source
declarations, and compiler or binary identities distinct.

The profile covers:

- Cargo package, crate-target, workspace-member, dependency-binding, and
  sysroot applicability;
- modules, reexports, inherent methods, traits, implementations, associated
  items, and generic declarations;
- generated and macro-expanded items with explicit portable, artifact-local,
  and unavailable boundaries;
- editions, compilers, targets, features, resolver versions, `cfg`, and
  compiler-option compatibility;
- exact, conditional, and declined metadata/binary mappings; and
- required vocabulary behavior, fail-closed outcomes, and scoped completeness.

- [Read the normative profile source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/rust/0.1/profile.md)
- [Open the profile payload schema](/schema/profiles/rust/0.1/schema.json)
- [Review the conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/rust-profile.md)
- [Inspect the complete fixtures](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures/valid)
