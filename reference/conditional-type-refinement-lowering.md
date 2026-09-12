# Conditional type-refinement consumer integration

This guidance accompanies `csmi.conditional-type-refinement` `0.1.0`; the
normative wire contract is in
`profiles/conditional-type-refinement/0.1/profile.md`. Python `TypeIs` and
`TypeGuard` are motivating projections, not CSMI wire names or a Bifrost API.

## Resolution and application

1. Dispatch on the exact vocabulary identifier, version, and schema. Validate
   the core document, profile payload, affected scope, and completeness before
   applying any fact.
2. Resolve the callable through its full CSMI symbol and artifact identity.
   Resolve the zero-based parameter ordinal against a complete callable shape.
   Names, source text, producer-local handles, and rendered signatures are not
   substitutes.
3. Resolve every reference in the structured target type through the same
   semantic model. Preserve ordered type arguments and reject a target whose
   identity or structure cannot be interpreted exactly. A profile-owned
   intrinsic additionally requires an exact required vocabulary use that the
   consumer supports.
4. Apply a supported fact only after call dispatch selects the exact callable.
   Multiple applicable overload facts must agree exactly; otherwise preserve a
   conflict and make no narrowing.

## Branch semantics

On a true result, `biconditional` intersects the incoming subject type with the
exact target type. `positive-only` replaces the incoming type with the target;
it must not assume subtype compatibility or intersect invariant generic types
into an impossible branch. On a false result, `biconditional` removes the target
type from the
incoming subject domain, while `positive-only` makes no refinement. Neither
mode proves that the call occurs, that it returns normally, or that the target
is inhabited.

The complement is relative to the consumer's proven incoming type; it is not a
portable standalone negated type. If the consumer cannot represent or compute
that complement soundly, the false branch remains uninterpretable or partial.

## Fail-closed and completeness behavior

Unsupported target forms, unknown type components, missing declarations,
ambiguous dispatch, conflicting overloads, cancellation, budget exhaustion,
and stale inputs prohibit complete coverage. Preserve those states separately
from a supported fact set, including an empty set. A consumer lacking this
required vocabulary must quarantine the affected callable/parameter scope; it
must not silently discard the facts and report no refinement.

Python's `TypeIs[T]` can project to `biconditional` only when the producer has
proved its specified two-branch meaning and exact `T`. `TypeGuard[T]` projects
to `positive-only`. Decorator names, return annotations parsed as text, or a
similar helper name do not establish either contract.

A Python method's `self` or `cls` maps to the core receiver, which is excluded
from the explicit parameter ordinal sequence. Bind the guarded argument through
the resolved callable shape, not the source parameter index. Preserve
`type[object]` as a structured target; this profile does not authorize erasing
generic arguments or treating an arbitrary structural target as a nominal class.
The [Python typing specification](https://typing.python.org/en/latest/spec/narrowing.html)
defines positive TypeGuard replacement and the distinct TypeIs intersection.

## Cross-language projection boundary

The [TypeScript narrowing handbook](https://www.typescriptlang.org/docs/handbook/2/narrowing.html#using-type-predicates)
also demonstrates user predicates narrowing both branches. A producer with an
exact resolved parameter predicate and target can project that two-branch
contract to `biconditional`, subject to the same dispatch, identity, agreement,
and completeness rules as Python TypeIs. Parameter names in the source must be
resolved to canonical ordinals; TypeScript structural targets require supported
structured identity or an exact required intrinsic vocabulary. A rendered
`parameterName is Type` annotation alone is insufficient evidence.

| Source contract | Retained fact | Left to the language adapter |
| --- | --- | --- |
| Python TypeIs | True intersection and false exclusion | Annotation identity, subtype validity, binding, generic substitution |
| Python TypeGuard | True replacement and unchanged false branch | Annotation identity, invariant generic semantics, binding |
| TypeScript parameter type predicate | Proven two-branch refinement | Predicate binding, structural type meaning, overload applicability |

These are manual mapping analyses. The repository wire consumer demonstrates
shared comparison and fail-closed behavior; no generated cross-language pack
or production adapter interoperability is claimed.
