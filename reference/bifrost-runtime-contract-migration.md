# Bifrost consumer adoption: portable runtime-values contracts

This checklist describes requirements for a Bifrost adapter to
`csmi.runtime-values` **0.2.0**. It is derived from the
[public profile contract](../profiles/runtime-values/0.2/profile.md), not an
audit of a particular Bifrost implementation or release. It makes no claim
about current consumer support, production model shipment, or deployment.
The same requirements apply to other adopting analyzers.

Core CSMI 0.1 and runtime-values 0.1.0 retain their existing contracts. This
specification extension changes no Bifrost product files or benchmark fixtures.

## 1. Negotiate and preserve the wire contract

Support 0.2.0 alongside 0.1.0 as distinct wire forms. Validate all five new fact
families, their scopes, required vocabulary uses, provenance, and references.
Implement import, export, semantic equality, and typed unsupported outcomes
together; preserve existing 0.1.0 round trips.

Portable applicability is not an optional artifact hash. Keep reviewed contract
content digests separate from actual artifact digests, retaining artifact-backed
models as explicit specializations. There is no general lossless downgrade:
selecting a portable contract does not produce runtime bytes.

Interpret exact context, key-comparison, and executable-identity schemes only
when their meanings are supported. A missing required scheme is invalid;
unsupported required semantics remain uninterpretable for affected units.
Unrelated core facts remain independently interpretable.

## 2. Establish the analyzed target

Resolve target evidence before selecting runtime endpoints. Associate supported
launch/build metadata or explicit user declarations with exact entries and
immutable source partitions. Keep declared compatible ranges separate from
observed deployment versions, and preserve unknown and mixed targets.

An `engines.node` constraint is useful only after a supported adapter establishes
which analyzed execution target owns that metadata. A build tool's dependency,
ambient typings, import spelling, or the analyzer host's runtime cannot silently
activate Node semantics throughout a project. Shared source may belong to
several target analyses without merging their results or erasing an unresolved
browser interpretation.

## 3. Evaluate one immutable activation snapshot

Evaluate whole-range applicability, all context and initialization constraints,
candidate completeness, externally supplied review/trust policy, explicit
disables, and potential conflicts. There is no implicit artifact-specific,
narrower-range, newer-version, or last-imported precedence.

Incomplete inventories remain indeterminate even when every known candidate is
disabled. Unknown evidence cannot become a match through a trust override.
Preserve conditionality and inactive/uncertain outcomes in diagnostics and
exported evidence, rather than translating them into an empty model.

## 4. Prove occurrence, store, and effect identity

Use resolver/binder evidence for roots, aliases, containers, static keys, loads,
result values, and observation points. A key selector filters already-proved
observations; query syntax does not create runtime identity. Qualify JavaScript,
TypeScript, and TSX source mappings separately.

Keep invocation, realm, backing store, key normalization, and key equality
explicit. Respect own-value versus inherited/accessor/proxy lookup, copied
versus shared environments, and platform-specific equality. Unknown equality
does not prove either aliasing or disjointness.

Track writes, deletes, conversions, exceptional behavior, and materialization
without reseeding an overwritten cell as pristine input. Exact observations
require dependency-closed initialization and effect evidence, including relevant
preloads, imports, native or unresolved calls, and interleavings. Missing proof
remains a typed limitation, not a special-case exclusion.

## 5. Invalidate caches and preserve evidence roles

Version persisted representations when their meaning changes. Cache inputs
must cover supported vocabulary/schema/comparator/identity-scheme versions,
normalized candidate contents (including rejected and potential overlaps),
target partitions and evidence, scoped review/trust policy, source/dependency
closure, store/key identity, and initialization/effect proof.

Stable local handles and active-record IDs alone cannot authorize cache reuse.
Keep authored content, activation snapshots, proof commitments, executable
identity, and actual artifact bytes distinguishable in storage and diagnostics.

## 6. Qualify consumer behavior independently

Run the [interchange conformance suite](../conformance/runtime-values-0.2.md),
then independently validate the adopting analyzer's binder, native runtime
mapping, mutation analysis, and user-facing policy route. Include arbitrary
environment names and supported argument indices, launch-mode-specific origins,
normal and exceptional paths, same and distinct keys, root/container
replacement, worker copies/sharing, unknown and mixed targets, explicit
disables, conflicts, unsupported schemes, and cache invalidation.

The checked-in corpus is synthetic wire-contract evidence. It does not attest
reviewer authority, runtime truth, deployment, or production adapter correctness.
A successful schema or reference-consumer test cannot replace those proofs.

## Security and benchmark boundaries

URI component encoding does not establish shell sanitization. Generic store
examples do not prove native environment persistence. A proof of no flow from
a write to one key into a read of a different key does not establish whole-program
cleanliness when the read key can independently contain external input.
Keep these claims separate and preserve frozen benchmark inputs, denominators,
and typed outcomes; do not introduce key exclusions or weaken completeness.
