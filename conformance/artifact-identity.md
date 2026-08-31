# Artifact identity conformance cases

These semantic cases are normative for the artifact-matching behavior in CSMI
0.1. Issue #9 will translate them into fixtures for the normative JSON
serialization.

## Matching cases

| Selector | Candidate evidence | Expected outcome | Reason |
| --- | --- | --- | --- |
| `pkg:pypi/example@1.2.0` | Equivalent canonical PURL | `matched` | Exact package and version agree. |
| `pkg:npm/example` plus `vers:npm/>=2.0.0\|<3.0.0` | `pkg:npm/example@2.4.1` | `matched` | Candidate is inside the VERS range. |
| Exact Cargo PURL plus required SHA-256 | Same PURL and matching digest over the declared archive | `matched` | Every conjunctive constraint agrees. |
| PURL without qualifiers | Equivalent candidate with additional qualifiers | `matched` | A broader selector may apply to a more specific candidate. |
| Two alternative selectors | One is contradicted and one matches | `matched` | Selectors are OR alternatives. |

## Near misses and inconclusive cases

| Selector | Candidate evidence | Expected outcome | Reason |
| --- | --- | --- | --- |
| `pkg:pypi/example@1.2.0` | `pkg:pypi/example@1.3.0` | `not matched` | Comparable exact versions disagree. |
| PURL plus required SHA-256 | Same PURL and a different digest over the same coverage kind | `not matched` | Exact content is contradicted. |
| npm VERS constraint | Candidate version, but the consumer lacks the npm VERS procedure | `indeterminate` | The consumer must not substitute lexical or SemVer comparison. |
| PURL plus required SHA-512 | Same PURL, but candidate bytes are unavailable | `indeterminate` | No constraint is contradicted, but a match cannot be established. |
| PURL requiring an architecture qualifier | Candidate does not expose architecture | `indeterminate` | Required qualifier evidence is missing. |
| Two alternative selectors | One is contradicted and one is indeterminate | `indeterminate` | No alternative matches and one remains possible. |

## Compatibility cases

| Artifact result | Compatibility evidence | Expected result |
| --- | --- | --- |
| `matched` | A required, understood runtime profile is satisfied | Applicability remains `matched`; compatibility is `compatible`. |
| `matched` | A required, understood runtime profile is contradicted | Applicability remains `matched`; compatibility is `incompatible`, and the model is not applied. |
| `matched` | The profile is understood but runtime evidence is missing | Applicability remains `matched`; compatibility is `indeterminate`, and the model is not applied by default. |
| `matched` | A required compatibility profile is unsupported | Applicability remains `matched`; the model is uninterpretable. |

## Invalid selectors

Each of these is semantically invalid rather than indeterminate:

- a malformed or non-canonical PURL;
- a PURL with a `subpath`;
- a selector with both a PURL exact version and a VERS constraint;
- a selector with neither an exact version nor a VERS constraint;
- a free-form version range;
- a non-canonical VERS string;
- a VERS scheme that does not apply to the PURL type;
- a digest with an unsupported core algorithm name but no declaring extension;
- two conflicting digest values presented for the same algorithm and coverage;
  or
- two alternatives whose semantic or completeness claims differ but are
  represented as one unscoped model.
