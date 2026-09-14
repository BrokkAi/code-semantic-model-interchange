# Portable runtime contract conformance

These cases govern `csmi.runtime-values` **0.2.0**. The schema validates
structure. `scripts/validate-runtime-values-0.2.py` validates document links,
provenance, recomputed identities, deterministic applicability, and evidence
consistency. Runtime truth and trust policy still require independently
reviewed inputs. The checked-in examples are conformance data, not a reviewed
production Node pack or actual deployment attestations.

## Applicability, trust, and overlap

| Input | Required outcome |
| --- | --- |
| Reviewed portable Node contract, exact supported declared target, same source partition, complete candidate set and trusted scoped review | Eligible conditional analysis; no artifact-byte or deployment verification claim. |
| Target range wholly contained in the reviewed range | Same conditional result for every permitted target version. |
| Target range partly overlaps the reviewed range | Indeterminate; an intersection does not cover the whole target. |
| Comparable incompatible version/platform/realm/module/launch context | Non-applicable for that target; do not erase other uncovered partitions. |
| Valid but unsupported comparison scheme | Unsupported; never guessed version order. |
| Malformed PURL/VERS or reversed/noncanonical interval | Invalid semantic document rather than valid unknown evidence. |
| Artifact-specific contract with matching actual digest and coverage | Eligible specialization, with artifact evidence separate from contract digest. |
| Artifact-specific candidate with missing bytes | Indeterminate; contract content hashes do not repair it. |
| Comparable artifact digest mismatch | Non-applicable specialization. |
| Identical behavior in portable and artifact-specific candidates | May coexist after both independently qualify. |
| Overlapping candidates disagree on key equality, lookup, origins, mutation or effects | Conflict; no last-wins, narrower-wins, newer-wins, or artifact-wins rule. |
| Missing review, wrong contract digest/partition/purpose, or explicit disable | Ineligible; record the reason and policy snapshot. |
| Matching candidate plus unresolved possible overlap or partial inventory | Incomplete activation; no false unique winner. |
| Host Node, package name, import, file extension, or typings with no target evidence | Unknown target; cannot activate the project. |
| Server and browser partitions in one project | Evaluate separately; Node facts cannot bind browser occurrences. |
| Shared source under both targets or unenumerated residual source | Preserve each target result and residual incompleteness. |

## Runtime observations

| Input | Required outcome |
| --- | --- |
| `process.env.CONFIG_TOKEN` and equivalent decoded bracket string | Same static key identity when the same exact store is proved; preserve source correspondence. |
| Another arbitrary own environment key | Governed by the same generic contract; no benchmark key inventory. |
| Static environment property resolves to inherited member, getter, or proxy | Excluded from own-environment behavior or incomplete if lookup is unresolved. |
| Static key absent from the own environment | No existing external value is invented; subsequent lookup behavior still matters. |
| `process.argv[7]` under a script-launch contract | Application-argument origin if present; index existence is not proved. |
| Script-launch `argv[0]` and `argv[1]` | Executable and entry metadata origins, independently from application arguments. |
| Eval/stdin/REPL/worker argv with only script-launch evidence | Non-applicable or unsupported mapping; no copied offset assumptions. |
| Dynamic key, computed index, symbol, unsupported coercion, optional chain | Typed incomplete/unsupported evidence remains in the inventory. |
| Parameter/local/import shadowing the global | Complete lexical exclusion is possible; no runtime-global value. |
| Reassigned root or replaced container | No stale exact runtime-container binding. |
| Known selected-key write, then read | Track written/conversion result; do not reseed pristine input. |
| Known normal deletion | Track deleted state and remaining lookup behavior. |
| Coercion invokes unknown user code or may fail | Separate normal/exceptional effects, with incomplete origin where required. |
| Unknown preload/dependency/native/async mutation | Open effect frontier; not complete merely because this file has no writes. |
| Known case-distinct keys on Windows main environment | Must use supported native equality; exact-string disjointness is unsound. |
| Windows worker copied environment | Case-sensitive copied store with copy-time value flow and separate later state. |
| Worker shared environment | Shared backing identity and concurrent effects; no assumed store isolation. |
| Unknown key equality or backing-store alias relation | Cannot prove stores/keys disjoint. |
| Host materialization, unknown exceptions, stale operation join, cancelled/budget-limited analysis | Partial/unknown observation; exact normal identity does not close other evidence. |
| Python `os.environ` mapping lookup | String for present key, missing-key exception; import-time snapshot and direct mapping writes retain their own contract. |

## Invalid documents and negotiation

Reject wrong family/kind/scope/version, unresolved references, missing required
vocabulary or provenance, wrong semantic digests, incompatible source owners,
empty ranges, exact observations before effects, and complete observations with
open effect/lookup/materialization evidence. Reject a portable contract carrying
an artifact-byte digest in its portable applicability form. Do not reject a
well-formed document simply because it records conflict or unsupported evidence.
Executable identities require explicit scheme/version fields; identical hash
text under different schemes is not an identity join. Equivalent local binding
aliases are allowed, but cannot hide contradictory claims about one exact
target/invocation/realm/load/point. Proof assertions and evidence commitments
are covered by a recomputed closure digest.

An older runtime-values 0.1-only consumer refuses affected 0.2 facts. A supported
consumer must preserve conditionality, all inactive/uncertain outcomes, exact
source/executable identities, review/trust decisions, and digest roles through
round trip. Shuffling semantic sets must preserve canonical identity; changing
contract behavior, target partition, candidate/review policy, source closure,
or effect evidence must change the relevant digest/cache input. An unchanged
local record ID does not authorize cache reuse.

The executable corpus covers the implemented interchange subset. The table is
also the consumer-adoption matrix: binder, native runtime, mutation, and
deployed-system cases require the adopting analyzer's own production tests.
Passing the schema cannot establish those program facts.

## Security and frozen benchmark distinctions

`encodeURIComponent` supplies URI component encoding. It does not justify a
shell sanitizer kill contract; shell taint and unknown effects stay explicit.
Generic store write/read examples do not prove native `process.env`
persistence.

A persistence test may write an argument value into one environment key, then
read a different key. A proof of no cross-key flow addresses that particular
persistence assertion. It does not establish whole-program cleanliness when
the read key can independently contain external environment input. Preserve
those separate semantic/adjudication results and any frozen fixture/denominator;
do not exclude keys or weaken completeness to fit a benchmark expectation.
