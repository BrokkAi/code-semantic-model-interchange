# Completeness and uncertainty conformance cases

These semantic cases are normative for CSMI 0.1 completeness statements.
Issue #9 will translate them into fixtures for the normative JSON
serialization.

## Coverage and absence

| Case | Expected coverage or inference | Reason |
| --- | --- | --- |
| Applicable model emits facts for a scope but no completeness statement | `unknown` | Positive facts remain usable, but omission is open-world. |
| Applicable model explicitly states `unknown` for an empty scope | `unknown`, not unavailable | The producer modeled the scope but made no exhaustiveness assertion. |
| Applicable model states `partial` with a limitation and emits no facts | `partial` | Empty partial discovery does not establish absence. |
| Partial procedure summary emits one transfer | The edge is usable; every omitted edge remains unknown | Completeness controls omission rather than positive-fact validity. |
| Complete procedure summary emits one transfer | The edge set is closed for that callable | Every required core transfer must be asserted or semantically covered. |
| Complete procedure summary emits an empty transfer set | No core may-information transfer applies | A complete empty set is an explicit family-scoped absence claim. |
| Complete empty transfer set | Effects, calls, exceptions, allocation, and purity remain unknown | Closed-world inference does not cross fact-family boundaries. |
| Complete `owner` declaration aspect with no owner fact | The declaration has no owner | The exact single-valued aspect is closed. |
| Complete `overrides` relationship scope with no relationships | No direct `overrides` relationship applies to that subject | Other predicates and transitive relationships remain open. |
| Complete artifact declaration-record scope for one identity scheme | Every declaration governed by that scheme is identified and present | An unidentifiable declaration would require partial or unknown coverage. |
| Complete conservative may-information set contains an extra edge | Coverage remains complete but may be imprecise | Completeness prevents omissions; it does not require minimality when the family permits over-approximation. |
| No applicable, interpretable model has facts or a statement for a requested scope | `unavailable` | Availability is a consumer outcome distinct from coverage status. |

## Combining applicable sources

| First source | Second source | Aggregate outcome |
| --- | --- | --- |
| Complete set | Compatible partial subset | `complete`; preserve both statements and provenance. |
| Complete set | Compatible unknown source with duplicate facts | `complete`; unknown omission does not weaken a covering complete claim. |
| Complete procedure-summary set | Additional compatible conservative transfer from a partial source | `complete` and less precise; retain the additional transfer. |
| Complete source omits one conservative transfer | Compatible partial source asserts that transfer | Retain the transfer and do not infer its absence from the complete source alone. |
| Partial set | Another partial set | `partial`, even if their union appears exhaustive. |
| Partial set | Unknown set | `partial`; no source establishes completeness. |
| Unknown set | Another unknown set | `unknown`. |
| No applicable source | No applicable source | `unavailable`, not `unknown`. |
| Two equivalent complete sets | Exact duplicate facts | One complete aggregate with both provenances preserved. |
| Complete exact relationship set omits an edge | Another source asserts that edge | Conflict; the affected aggregate is uninterpretable. |
| Two complete single-valued declaration-aspect sets disagree | Different known values | Conflict; a consumer must not choose a producer. |
| Complete claims apply to different artifact versions | Both packages share a display name | Claims remain separate and do not combine. |
| Narrow complete scopes appear to cover a broader scope | Family defines no scope-composition rule | The broader scope is not complete. |

## Near misses and fail-closed outcomes

| Statement or consumer behavior | Expected outcome | Reason |
| --- | --- | --- |
| `partial` statement has no limitation | Semantically invalid | Partial coverage must preserve at least one typed reason. |
| One model repeats an equivalent family and scope or assigns it both `partial` and `complete` | Semantically invalid | A family-scope tuple has exactly one producer coverage status. |
| `complete` statement contains `budget-exhausted`, `cancelled`, or another limitation | Semantically invalid | A limiting condition and complete coverage are contradictory. |
| `other` limitation has no non-empty diagnostic explanation | Semantically invalid | The generic kind must still preserve actionable producer evidence. |
| Consumer encounters an unrecognized limitation kind | Preserve the status and report the unrecognized kind | Limitation detail cannot promote or erase typed coverage. |
| Producer claims complete after an unresolved required symbol, unavailable input, or unsupported relevant construct | Non-conforming producer | Known coverage gaps prohibit a complete claim. |
| Producer emits facts after cancellation but cannot attest their validity | No semantic model may be emitted from that operation | Partial status cannot launder unreliable facts. |
| Consumer turns budget exhaustion into a complete empty set | Non-conforming application | Failure is typed incompleteness, not evidence of absence. |
| `unknown` or `partial` omission is interpreted as a negative fact | Non-conforming application | Neither status licenses closed-world inference. |
| Empty fact array with no completeness statement is interpreted as complete | Non-conforming application | Structural emptiness defaults to unknown coverage. |
| Complete transfer set is interpreted as proof that the callable cannot throw or mutate | Non-conforming application | Completeness applies only to `procedure-summaries`. |
| Statement uses a display name, wildcard string, or analyzer query as its scope | Semantically invalid core scope | Scope must use portable artifact and symbol identity. |
| Statement uses the wrong scope shape for its fact family | Semantically invalid | Each family defines its exact scope grammar. |
| Statement names an unsupported required family or profile | Uninterpretable | Encoded text cannot substitute for semantic support. |
| Artifact applicability is indeterminate but the complete claim is used | Non-conforming application | Negative inference requires matched applicability. |
| Consumer-resolved local facts promote a producer's partial statement to complete | Non-conforming application | Supplementation does not rewrite producer coverage. |
| Two partial sources are promoted to complete because no obvious gap remains | Non-conforming aggregation | Only a valid covering complete claim licenses completeness. |
| Conflicting complete sources are reduced to partial and processing continues | Non-conforming aggregation | A contradiction is observable and uninterpretable, not weaker coverage. |
| A trust score or confidence extension changes `partial` to `complete` | Non-conforming application | Confidence and trust are orthogonal to coverage. |
| Free-form version or runtime condition is embedded in the statement | Semantically invalid core claim | Variants belong in artifact applicability or semantics from a vocabulary use declared `required`. |
| A generic negated fact is emitted without family-defined profile semantics | Semantically invalid | Core absence is expressed through a complete scoped set. |
| A profile-defined negative fact is emitted under `unknown` or `partial` coverage | Semantically invalid | Explicit negative facts require an applicable complete claim for their family and scope. |

## Interoperability obligations

A producer and consumer must agree on the fact family, scope identity, status,
vocabulary uses declared `required`, fact equality, conflict, and
coverage/subsumption rules
before using a completeness statement. Unsupported semantics remain
uninterpretable rather than empty.

Consumers must preserve per-source statements, limitations, and provenance
even when they derive an aggregate status. Aggregate completeness never grants
broader applicability, stronger fact semantics, or completeness in another
family.
