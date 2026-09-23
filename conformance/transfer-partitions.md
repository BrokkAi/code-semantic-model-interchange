# Transfer partition coverage conformance

This suite is normative for `csmi.transfer-partitions` `0.1.0`. Full Python and
JavaScript documents are in `fixtures/valid/transfer-partition-python.json` and
`fixtures/valid/transfer-partition-javascript.json`. Both use their existing
language identity schemes with required profile uses, one input parameter, one
normal result, an explicit empty core summary, callable-wide core `partial`,
and a complete `all-inputs` normal-result partition. Their symbols and package
selectors differ; the claimed transfer semantics are identical. The source
idiom is respectively `def constant(value): return 7` and
`export function constant(value) { return 7; }`. Those snippets motivate
manually reviewed claims; they are not source-analysis output or execution
proof. A producer that has not examined possible exceptional and caller-visible
transfers MUST keep core callable coverage partial even for these idioms.

| Case | Expected consumer outcome |
| --- | --- |
| Complete `all-inputs` `result[0]`, explicit empty core summary | No reported core input-to-`result[0]` flow. |
| Same document queried for an input-to-`exception` edge | Out of scope; exceptional transfer and exception occurrence remain unknown. |
| Same document queried for post-state `parameter[0]` or `result[1]` | Out of scope; no inference. |
| Same document queried for an effect or callback invocation | Out of family; no inference. |
| Complete `input-root parameter[0]` claim queried for that root | Closed for that root and result only. |
| Complete `input-root parameter[0]` claim queried for another root | Unknown; root claims do not compose into `all-inputs`. |
| `all-inputs` and one `input-root` at the same result | Overlap; `all-inputs` covers the narrower claim. |
| Two different input roots at one result | Disjoint edge sets, even if their runtime values may alias. |
| Same source and different normal result positions | Disjoint partitions; one result does not cover another. |
| Duplicate equivalent claims in one model, including different statuses | Semantically invalid. |
| Two compatible complete claims across applicable models | Complete; retain both provenances and union compatible positive edges. |
| Complete empty and an additional compatible conservative positive edge from another source | Retain the edge; it blocks a negative inference for that candidate. |
| Incompatible exact versions, identities, or applicability | Uninterpretable or indeterminate, never a preferred winner. |
| Partial with `budget-exhausted` and empty summary | `partial`; omission remains unknown. |
| Relevant unresolved callee or unknown callback | `partial` with typed limitation; a complete producer claim is nonconforming. |
| Positive established edge under partial coverage | Edge remains usable; other omissions remain unknown. |
| Unsupported required profile version | Partition claim uninterpretable; core positive edges can remain usable. |
| Missing required use or invalid scope/root | Semantically invalid; schema rejects malformed scope syntax. |
| No claim for the partition | `unknown` in an applicable model; empty summary is not a negative claim. |

`scripts/validate-transfer-partitions.py` independently consumes the full
documents and exercises permitted and forbidden inference. Profile schema
fixtures under `profiles/transfer-partitions/0.1/fixtures` test valid and
near-miss scope syntax. This profile only partitions conservative core
may-information transfers. It never asserts absence of effects or runtime
execution behavior.
