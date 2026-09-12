---
title: Conditional type refinement 0.1
description: Exact callable predicates that refine one parameter to a structured target type.
---

`csmi.conditional-type-refinement` version `0.1.0` models the branch-sensitive
type meaning of an exact predicate callable. Each fact identifies the exact
callable, a zero-based parameter ordinal, and an exact structured target type.

`biconditional` semantics refine the true branch to the target and the false
branch to its complement within the incoming subject type. `positive-only`
semantics refine only the true branch. These correspond to the portable meaning
needed for Python `TypeIs` and `TypeGuard`, without adding either language form
to CSMI core.

Unsupported targets, unresolved identities, conflicting overloads, and
uninterpretable required versions fail closed. They never become empty facts or
complete no-refinement claims.

- [Normative profile](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/conditional-type-refinement/0.1/profile.md)
- [Payload schema](/schema/profiles/conditional-type-refinement/0.1/schema.json)
- [Conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/conditional-type-refinement.md)
- [Consumer integration](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/reference/conditional-type-refinement-lowering.md)
