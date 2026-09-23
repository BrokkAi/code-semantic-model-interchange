# Core transfer partition coverage profile 0.1.0

This normative standard profile assigns `csmi.transfer-partitions` exact version
`0.1.0` and schema
`https://csmi.brokk.ai/schema/profiles/transfer-partitions/0.1/schema.json`.
It depends only on CSMI core `0.1` / `0.1-json` and adds no core field, transfer
relation, effect, or language-specific identity. BCP 14 key words apply.

## Contract crosswalk

| Existing grammar | Can close input-to-one-normal-result transfers? | Reason |
| --- | --- | --- |
| Core `procedure-summaries` scope `{callable}` | No | `complete` closes **every** core transfer of the callable; limitations do not narrow scope. |
| Core declaration and relationship scopes | No | They govern different fact families. |
| `csmi.structured-locations` projection | No | It refines locations; its coverage remains callable-wide core coverage. |
| `csmi.collection-flow` scope `{callable}` | No | It closes its own collection-flow family, not the core transfer subset. |
| `csmi.value-transfer` | No | It qualifies individual transfer meaning; it supplies no normal-result coverage scope. |

## Attachment and membership

The sole attachment is a namespaced `completenessStatements[]` entry with
`vocabulary: "csmi.transfer-partitions"`, `version: "0.1.0"`, and
`family: "transfer-partitions"`. Its `scope` MUST validate against this schema.
The enclosing model MUST declare an exact `vocabularyUses[]` entry with this
schema URI, `requirement: "required"`, and a `fact-family` affected unit whose
family and scope equal the statement. The use affects the partition claim only;
the core summary and unrelated units remain independently interpretable.
No `extensionFacts[]` payload exists in this version. The family's positive
facts are precisely the applicable, interpretable core `procedureSummaries[]`
may-information transfers whose source and destination lie in the scope.
Statements do not emit or alter transfers. Every claim MUST name an exact local
callable symbol resolving to a callable with a complete shape, and an applicable
core procedure summary for that callable, including an explicit empty summary
when there are no transfers. Core provenance, artifact applicability, required
projection uses, and identity comparison continue to apply.

## Scope and inference

`exit: "normal"` and destination `output result[n]` mean the whole logical
normal result at declared position `n`, including every supported projection
beneath that root. No exceptional value, caller-visible receiver/parameter/
capture post-state, callback result, or other normal result belongs to the
scope. This version defines no scope for those exits or outputs. A producer
MUST NOT present them as covered through a limitation or destination spelling.

`source: {"kind":"all-inputs"}` includes the whole input receiver (if any),
every declared input parameter, and every captured input value or storage
location of the callable, including their supported projections. A producer
MUST establish the relevant capture universe before claiming this scope
complete. `source: {"kind":"input-root","root":...}` restricts the source
to the complete selected input receiver, parameter, or capture root and its
supported projections. The root MUST exist under the callable shape and core
capture identity rules. Root selectors do not select individual call-site
arguments, runtime objects, or paths. Producer-local identifiers, names,
source text, and rendered signatures cannot prove these identities.

A complete statement asserts that all core may-information transfers from the
selected source universe to the selected whole normal result are emitted or
semantically covered under the applicable core projection subsumption rules.
For an omitted candidate edge inside that exact partition, a consumer MAY infer
no reported core may-information transfer only after matched applicability,
supported identities and projections, and conflict checks. In particular a
complete empty `all-inputs` partition permits no input-to-that-normal-result
flow. This says nothing about constant results, exceptions, effects, mutation,
purity, runtime execution correctness, or any other output. A core
`procedure-summaries` claim remains `unknown` or `partial` unless separately
and legitimately complete for the entire callable. Conversely, callable-wide
core completeness can cover this partition if all profile semantics are
supported; it does not require a duplicate partition statement.

## Equality, overlap, conflict, and merge

Scope equality requires the same artifact applicability, callable structural
identity, exact profile version, destination position, and source selector.
Input capture roots compare by core structural symbol identity, not local
reference spelling. Distinct destination positions are disjoint in this
family. At the same destination, `all-inputs` contains every valid `input-root`
scope. Two unequal specific input roots are disjoint as *root-indexed edge
sets*, even if runtime values alias; an edge is still indexed by its source
root. A selected root covers all its supported projections. No other overlap
or subsumption is defined; unknown identity, unsupported projections, or
indeterminate applicability prevent a comparison and negative inference.

Within one model, duplicate equivalent family/scope statements or incompatible
statuses are semantically invalid under core section 3.5. Across models,
compatible positive core may-transfers are unioned, retaining provenance;
additional conservative edges can reduce precision. Equivalent complete
claims combine as complete. A covering complete `all-inputs` claim covers a
narrower root claim, provided all other evidence is compatible. A specific
root claim cannot cover `all-inputs`. Conflicting exact profile versions,
identity evidence, applicability, or transfer semantics make the affected
aggregate uninterpretable; consumers MUST NOT select a preferred source or
silently drop the disagreement. Contradictions under core section 3.5 remain
contradictions. Two partial claims never yield complete coverage. This version
defines **no composition** of separate root claims into `all-inputs`, separate
result claims into a callable, or this family into an effect family, even when
the observed lists appear exhaustive.

## Incomplete analysis and versioning

Recursion, widening, and unresolved callees are permissible for a complete
claim only if the producer establishes conservative coverage of every relevant
may-transfer in this exact partition. A recursion cut, widening that loses a
relevant source/destination possibility, unresolved relevant callee or callback,
unavailable input, unsupported projection, cancellation, budget exhaustion,
or producer error that leaves relevant possibilities unexamined prohibits
`complete`. Emit `partial` with a core typed limitation, or `unknown` if no
exhaustiveness assertion is possible. Established positive edges remain usable;
unsupported or cancelled analysis MUST NOT invent an edge. A limitation on one
partition does not automatically limit a disjoint proven partition. Widening
precision is independent from coverage only when the emitted conservative
edges still cover every possibility.

Consumers without this exact required profile version MUST report each affected
partition claim as uninterpretable. They MAY still use separately interpretable
core positive transfers and core coverage. They MUST NOT reinterpret the claim
as a core callable claim, `unknown`, or complete-empty. This is a new opt-in
profile version; existing CSMI documents need no migration and core version
`0.1` and schema `0.1-json` remain unchanged. Any future change to this scope
grammar or negative inference requires a new exact profile version and schema
identity. This profile does not standardize analyzer caches.

## Independent evidence

Python and JavaScript examples with identical partition meaning and near misses
are in `conformance/transfer-partitions.md`. The independent small consumer in
`scripts/validate-transfer-partitions.py` parses full documents, validates this
scope and implements permitted and forbidden negative inferences. The examples
are manually authored interchange evidence, not a claim that either language
producer is integrated or that runtime behavior has been proven.
