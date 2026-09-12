# Conditional type-refinement conformance

These obligations accompany `csmi.conditional-type-refinement` `0.1.0`.
Structural acceptance, semantic validity, artifact applicability, dispatch
resolution, and consumer support are separate outcomes.

| Case | Required result |
| --- | --- |
| Exact callable and zero-based parameter ordinal | Apply only to that parameter of that callable after full CSMI identity and artifact matching. |
| Same display name or rendered signature | No application without exact resolver-proven identity. |
| Exact structured target type | Preserve the full type expression, including referenced symbol identity and ordered arguments. |
| Intrinsic target without an exact required vocabulary use | Treat the refinement as uninterpretable. |
| `biconditional` mode and true result | Refine the subject to the target type. |
| `biconditional` mode and false result | Refine the subject to the complement of the target within the subject's incoming type. |
| `positive-only` mode and true result | Replace the incoming type with the target, including non-subtype invariant generic targets. |
| `positive-only` mode and false result | Make no refinement; do not infer the complement. |
| Target not representable exactly | Preserve a typed unsupported outcome; do not emit a weaker target or an empty fact. |
| Callable or parameter cannot be resolved | Treat the affected scope as uninterpretable. |
| Incomplete applicable overload set or missing candidate fact | Preserve uncertainty and apply no narrowing. |
| Equivalent duplicate facts | Deduplicate without adding evidence or creating a conflict. |
| Conflicting applicable overload facts | Preserve a conflict and apply neither candidate; document order never chooses truth. |
| Unsupported required profile version | Treat the exact affected callable/parameter scope as uninterpretable. |
| Empty or omitted facts | Keep the family open-world unless a separately valid completeness statement closes the exact scope. |
| Complete scope with unsupported, unresolved, conflicting, cancelled, stale, or budget-exhausted evidence | Reject the completeness claim. |

The executable suite MUST include both refinement modes, a parameter-ordinal
near miss, a structured generic target, structural rejections, conflicts, an
unsupported target, an unsupported vocabulary version, and complete versus
partial document cases. Passing schema validation does not certify a language
adapter or dispatch resolver.
