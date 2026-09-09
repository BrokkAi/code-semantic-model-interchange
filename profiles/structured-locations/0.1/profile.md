# Structured procedure-summary locations profile 0.1.0

This document defines `csmi.structured-locations` version `0.1.0`. Its
normative schema is `profiles/structured-locations/0.1/schema.json`, identified
by `https://csmi.brokk.ai/schema/profiles/structured-locations/0.1/schema.json`.
The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**,
and **MAY** are interpreted as BCP 14.

## 1. Scope and negotiation

The profile supplies one concrete projection scheme for core procedure-summary
locations. A vocabulary use MUST be `required` and MUST affect core slot
`procedure-summary-projection` for each exact callable whose summary uses the
scheme. A consumer that does not support this exact version MUST report the
affected summary as uninterpretable. It MUST NOT drop the projection or replace
it with the boundary root.

This profile adds no new root or transfer relation. Core input receiver,
parameter, and capture roots; output receiver, parameter, capture, result, and
exception roots; directional may-information transfer; provenance; and
`procedure-summaries` completeness retain their CSMI 0.1 meanings.

## 2. Bounded paths and precision

A path contains from one through sixteen ordered steps. Every producer and
consumer MUST enforce this bound. A longer concrete path may be represented by
retaining a sound prefix followed by `summary-tail` with cause `path-limit`; it
MUST NOT be silently truncated.

An exact path has neither an `any` selector nor `summary-tail`; its serialized
steps denote the whole projected location and every step selects one
sublocation. A summarized or widened path contains an `any` selector or final
`summary-tail` and may denote multiple locations or unretained suffixes. Each
marker preserves a typed cause. `key(any)` uses `unknown-key`, `index(any)` uses
`unknown-index`, and an `any` selector or `summary-tail` MUST be the final step.
Unknown,
unresolved, or ambiguous identity MUST NOT be repaired with source text,
display names, rendered signatures, regexes, or producer-local identifiers.

Precision and coverage are independent. A summarized conservative path can be
part of a complete core transfer set. Cancellation, budget exhaustion, stale
inputs, unsupported relevant semantics, or incomplete discovery instead
prohibit complete `procedure-summaries` coverage and belong in that statement's
typed limitations.

## 3. Steps

`field` selects storage identified by one local CSMI symbol. The symbol MUST
resolve to a `value` declaration under a stable, applicable symbol identity.

`key` selects an associative sublocation. An exact selector is one input
`parameter[n]` or input `capture` value from the same callable. `any` denotes
all possibly selected keys. The profile deliberately does not serialize
language-specific hashing, borrowing, equality, or key-conversion rules; a
language/ecosystem profile must prove that a call-site key denotes the same
key identity before applying an exact selector.

`index` selects a sequential sublocation. It accepts the same boundary-value
selectors, a non-negative mathematical-integer `constant`, or `any`. A
constant has mathematical integer equality and no source-language numeric type
or coercion semantics. A consumer that cannot represent it exactly MUST report
the summary as uninterpretable or conservatively widen it while preserving the
original fact and report the widening.

`variant-payload` selects one zero-based payload position of an exact
resolver-proven variant symbol. The variant MUST resolve to a local `value`
declaration. This models sum-type and tagged-union payloads without making any
language's enum representation core. It does not assert that the variant is
constructed, matched, returned, thrown, or the only possible outcome.

Steps compose left to right. Exact path equality requires equal roots, scheme
and version, steps, and referenced symbol keys or boundary slots.
Different exact keys, indices, fields, variants, or payload positions do not
overlap. An `any` key or index overlaps each selector of the same kind at that
position. A summarized tail overlaps every longer path sharing its retained
prefix. No other overlap or subsumption is implied.

## 4. Procedure-summary patterns

An associative write can transfer `parameter[value]` to output
`receiver.key(parameter[key])`. A matching read can transfer input
`receiver.key(parameter[key])` to a normal result. A sequential append can
transfer a value to output `receiver.index(any)`; because the new index is not
identified, that endpoint is summarized. A wrapper constructor can transfer a
parameter to output `result[0].variant-payload(variant, 0)`.

Immediate exceptional exits continue to use the core output `exception` root.
A normally returned error or alternative variant uses `variant-payload` under
the normal result root and MUST NOT be rewritten as an exception. Profile
projections do not assert exit reachability; constant exceptional behavior
requires a separately versioned effect/control contract.

## 5. Provenance, completeness, and merging

Every referenced callable, capture, field, and variant uses the enclosing
model's stable symbol keys and artifact applicability. Transfer-level,
summary-level, model-default, and completeness provenance remain core CSMI
provenance. A projection does not mint a second callable or heap identity.

Facts merge only after artifact applicability, callable identity, callable
shape, projection support, and every referenced symbol or boundary slot agree.
Exact paths may be subsumed by a compatible summarized path, reducing
precision but not strengthening coverage. Two partial sources never combine
into complete coverage without a valid covering complete claim. Unsupported
required profile semantics are uninterpretable, never an empty or root-level
transfer.

## 6. Explicit non-goals and cleanup prerequisite

The profile does not define source lowering, receiver resolution, dispatch,
macro expansion, destructuring, question-mark or comparable control flow,
object identity, aliasing, mutation, allocation, ownership, escape, lifetime,
destructor scheduling, or implicit cleanup.

A generalized type-level destructor/cleanup contract does not belong in this
location profile. It requires an independently versioned ownership/lifetime
and invocation-effect profile defining the exact type/member identity,
implicit-call boundary, may/must modality, reachability and non-rejoining exit
behavior, coverage, conflicts, and merge rules. Until a consumer has that
contract and the language evidence needed to apply it, cleanup-related
completeness gaps remain typed incompleteness; container summaries MUST NOT
discharge them heuristically.

## 7. Relationship to collection-flow

`csmi.collection-flow` 0.1.0 defines keyed receiver shapes, entry/value
observations, generic substitution, and higher-order callback transfer inside
its own `collection-flows` fact family. This profile instead supplies a small
direct projection scheme for core procedure-summary endpoints, including
sequential indices and variant payloads. Neither vocabulary use implies the
other. A producer emitting both MUST establish that their facts are compatible
and preserve their independent completeness scopes; a consumer MUST NOT
translate one into the other from matching step names or apparent structure.
