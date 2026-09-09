# Structured procedure-summary location conformance cases

These cases are normative for `csmi.structured-locations` 0.1.0.

## Positive cases

| Case | Interpretation |
| --- | --- |
| Input `parameter[1]` to output `receiver.key(parameter[0])` | The value may reach the receiver cell selected by the same declared key parameter. |
| Input `receiver.key(parameter[0])` to output `result[0]` | The result may depend on the selected associative cell. |
| Two otherwise equal paths use `parameter[0]` and `parameter[1]` | They are distinct exact sublocations; no overlap is inferred without separately proven key equivalence. |
| Input value to output `receiver.index(constant 0)` | The value may reach the exact mathematical-integer index. |
| Input value to output `receiver.index(any)` with `unknown-index` | The value may reach any indexed sublocation; the endpoint is summarized. |
| Input value to output `result[0].variant-payload(V, 0)` | The value may reach payload position zero of exact variant symbol `V` in a normally returned wrapper. |
| Input value to output `exception` | This remains an ordinary core transfer to the immediate exceptional boundary; the profile adds nothing. |
| A sound prefix followed by `summary-tail(path-limit)` | Every longer location under the retained prefix may be denoted. |

## Rejections and fail-closed cases

| Case | Outcome and reason |
| --- | --- |
| A seventeenth step | Structurally invalid; paths are bounded at sixteen steps. |
| `key(source-text "key.clone()")` | Structurally invalid; source spelling is not key identity. |
| `variant-payload` contains `variantName` rather than a symbol | Structurally invalid; display names do not prove variant identity. |
| A referenced parameter position is absent from the callable shape | Semantically invalid. |
| A field, capture, or variant reference does not resolve to a local `value` declaration | Semantically invalid. |
| `any` or `summary-tail` is followed by another step | Semantically invalid; the summarized remainder must be terminal. |
| A required vocabulary use is missing, optional, or targets another callable | Semantically invalid and the affected summary is uninterpretable. |
| A consumer drops an unsupported projection and applies the root transfer | Non-conforming; it has changed the abstract location. |
| A normal error variant is mapped to core `exception` | Incorrect; variant payload and immediate exceptional exit are different boundaries. |
| A summarized endpoint appears in a complete transfer set | Permitted; conservative precision and fact-set completeness are independent. |
| Cancellation or budget exhaustion is encoded only as path widening | Non-conforming; operation incompleteness belongs in typed core coverage limitations. |
| A container summary is used to dismiss an implicit-cleanup gap | Non-conforming; this profile defines no ownership, lifetime, or cleanup behavior. |

## Interoperability obligations

Producer and consumer must agree on exact artifact and callable identity,
callable shape, profile version, stable referenced symbols, boundary-slot
binding, selector equality, overlap and subsumption, the sixteen-step bound,
and core provenance and completeness. Language-specific key equivalence,
receiver resolution, lowering, ownership, and cleanup evidence remain explicit
consumer/profile prerequisites and cannot be inferred from similar names.
