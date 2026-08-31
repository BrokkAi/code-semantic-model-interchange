# Procedure-summary conformance cases

These semantic cases are normative for CSMI 0.1 procedure summaries. Issue #9
will translate them into fixtures for the normative JSON serialization.

## Valid boundary locations and transfers

| Case | Expected interpretation | Reason |
| --- | --- | --- |
| Input receiver to output `result[0]` | Information from the receiver may influence the first normal result | The receiver is a first-class input root. |
| A projected input receiver field to output exception | Information from receiver-reachable state may influence an immediate exceptional result | Receiver projections use the same versioned location mechanism as other roots. |
| Input `parameter[0]` to output `result[0]` | Information from the declared first parameter may influence the first normal result | The core relation is directional may-information transfer. |
| Python `def f(*, value, strict)` called as either `f(strict=True, value=x)` or `f(value=x, strict=True)` | `value` binds to `parameter[0]` and `strict` binds to `parameter[1]` in both calls | Parameter positions come from the declaration, not call-site label order. |
| A positional-or-named argument supplied by label | It binds to the same declared `parameter[n]` as a positional use | Labels select declaration slots; they do not create named-only ports. |
| A variadic-positional or variadic-named declaration | The entire collected argument sequence or mapping has one declared parameter root | Individual supplied arguments do not create extra parameter positions. |
| Projection from a variadic parameter to one collected element under a supported scheme | The projected element is a valid abstract source location | Element selection belongs to the projection scheme. |
| Input parameter to a projected output receiver field | Information may reach externally visible receiver post-state | A supported field scheme gives the nested location portable meaning. |
| Input parameter to both output `result[0]` and output `result[1]` | Both logical results may depend on the parameter | Multiple logical results use declaration positions independently. |
| One output result projected to a tuple or record component | The callable still has one logical result | Source-level destructuring does not create additional result slots. |
| Input capture to output result | Information from captured storage may influence the result | The capture is named by stable value-symbol identity. |
| Input parameter to output exception | The parameter may influence an immediately thrown or raised value | Exceptional transfer crosses the invocation boundary directly. |
| Input parameter to a projected normal Promise result | Information may influence the later fulfillment value under the required async projection profile | The unprojected normal result remains the returned Promise wrapper. |
| Rust input parameter to an `Ok` or `Err` projection of output `result[0]` | Either wrapper variant may carry information from the parameter | Rust `Result` is a normal wrapper rather than an immediate exception. |
| Duplicate copies of the same source and destination edge | One semantic transfer | Transfer collections are unordered sets. |
| Constructor parameters to a profile-defined constructed result | Information may reach the constructed value without an input receiver | Ownership by a type does not create a pre-existing constructor receiver. |
| Derived, encoded, aggregated, or conditionally selected output | The ordinary core edge remains a valid may-information transfer | Core does not promise value preservation or unconditional flow. |

## Near misses and fail-closed outcomes

| Summary or application | Expected outcome | Reason |
| --- | --- | --- |
| Output `result[0]` to input `parameter[0]` | Semantically invalid | A core source must be input phase and a destination must be output phase. |
| Input parameter to output result is present | Do not infer the reverse edge | Core edges are directional. |
| Input parameter to output result is present | Do not infer equality, aliasing, mutation, exact preservation, or must-flow | Those meanings are deliberately outside the core relation. |
| `f(strict=True, value=x)` binds the first spelled argument to `parameter[0]` | Incorrect application | The `strict` label resolves to its declared position even when spelled first. |
| A named-only parameter is represented by its label instead of `parameter[n]` | Semantically invalid core root | Labels are binding evidence; the canonical root is the declaration position. |
| Three arguments are collected by one variadic-positional declaration and represented as three new parameter positions | Semantically invalid | The declaration has one variadic root; elements require projections. |
| Parameter or result position is negative, absent, or outside the callable shape | Semantically invalid | Summary slots cannot extend the declaration shape. |
| Receiver root appears for a receiver-free static or associated function | Semantically invalid | Ownership does not establish a receiver. |
| Receiver is encoded as `receiver[0]` or as `parameter[0]` | Semantically invalid | Receiver roots have no index and are separate from the declared parameter sequence. |
| Unprojected output parameter has no required by-reference or writeback profile | Uninterpretable | Ordinary local parameter reassignment is not caller-visible post-state. |
| Non-empty projection names an unsupported scheme or version | Uninterpretable, not an edge at the root | Dropping the path would change the location's meaning. |
| Projection contains an opaque producer heap-node ID or database row ID | Semantically invalid portable location | Analyzer-internal identity has no cross-tool equivalence. |
| Projection uses a field display name without a scheme that establishes stable identity | Semantically invalid or uninterpretable | Textual resemblance is not resolver-proven location identity. |
| Rust `Err` is represented as output `exception` without a required language profile | Incorrect model | It is normally one variant of a normal result wrapper. |
| A normally returned rejected Promise is represented as an immediate output `exception` | Incorrect model | Promise rejection occurs through later async semantics. |
| A callback invocation is encoded as a transfer to its argument | Incorrect core model | Invocation is an effect; any related transfer needs an applicable effect/profile contract. |
| A summary for one callable is applied to an override or same-named callable | Inapplicable unless a required profile proves an inheritance rule | Exact symbol identity is the core application boundary. |
| Missing or uninterpretable summary is silently replaced with all-arguments-to-all-outputs edges | Non-conforming application | Unknown-call supplementation must be a named, observable local policy outside the CSMI transfer set. |
| Empty transfer set is treated as proof that the callable is pure or has no flow | Incorrect interpretation | Absence is unknown until a matching completeness claim says otherwise. |
| Conditional may-transfer is omitted because the producer cannot encode its path condition | Potentially incomplete summary | A possible conditional transfer can be represented conservatively as an unguarded core edge. |

## Interoperability obligations

A producer and consumer claiming procedure-summary support must agree on the
callable symbol and complete callable shape before binding ports. For every
non-empty projection path they must also agree on the projection scheme and
version, including equality, overlap, subsumption, composition, and mapping to
the consumer's memory abstraction.

Unsupported declaration evidence, projection semantics, or required profiles
must remain observable as uninterpretable or incomplete. Consumers may layer a
separately named unknown-call policy over their own analysis, but must preserve
the imported summary, applicability, provenance, and completeness independently.
