# Collection-flow conformance

These obligations accompany `csmi.collection-flow` `0.1.0`. Run
`python3 scripts/validate-collection-flow.py` for the executable schema,
cross-record, and projection cases. Structural acceptance, semantic validity,
artifact applicability, and consumer support remain separate outcomes.

| Case | Required result |
| --- | --- |
| Exact generic receiver with two structured arguments | Substitute the declaration's exact ordered parameter identities recursively. |
| Nested generic argument | Preserve the nested reference and its ordered arguments. |
| Same display name but different artifact or type identity | No matching substitution. |
| Raw receiver or missing generic argument | Unknown or unsupported substitution; no fabricated argument. |
| Input value transferred to a parameter-selected keyed value | May-information transfer to the selected abstract entry value; no strong update or alias guarantee. |
| Aggregate entry selection | Abstract set including zero entries; no guaranteed invocation or order. |
| One entry delivered to callback parameter zero | Distinct callback invocation input, not enclosing output parameter zero. |
| Two callback parameters receive key and value separately | Preserve two positions; do not invent a product argument. |
| Explicit product component zero or one | Preserve component identity and lower into resolver-proven consumer bindings. |
| Entry without product evidence | Do not infer component zero means key. |
| Wrong callback position or missing callable shape | Reject semantic application rather than guess the boundary. |
| Complete profile scope retaining a semantic gap | Reject the completeness claim. |
| Duplicate equivalent facts | No additional semantic weight. |
| Conflicting supported facts or multiple callback candidates | Preserve ambiguity; input order never selects truth. |
| Unsupported exact required profile version | Affected units are uninterpretable, not empty. |
| Budget exhaustion or cancellation | Preserve typed incompleteness; positive evidence does not certify exhaustiveness. |

See [ecosystem mappings](../reference/collection-flow-ecosystems.md) for
primary-source API evidence and language-specific near misses. Reference
producer/consumer exercises demonstrate the portable algebra; they do not
certify production compiler adapters or end-to-end Bifrost lowering.
