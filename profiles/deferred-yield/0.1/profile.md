# CSMI deferred-yield profile 0.1.0

This normative document assigns `csmi.deferred-yield` exact version `0.1.0`
and schema `https://csmi.brokk.ai/schema/profiles/deferred-yield/0.1/schema.json`.
It is an analyzer-neutral standard vocabulary under core section 3.6. It does
not change CSMI core `0.1`, serialization `0.1-json`, or the during-call
semantics of `csmi.collection-flow` `0.1.0`.

## Linked scope, identity, and applicability

Each fact is one `extensionFacts[]` record with family `deferred-yields` and
exact scope `{ "factory": <symbol>, "resume": <symbol>, "handleType":
<symbol> }`. The payload repeats those exact local symbols. The vocabulary use
MUST be `required`, name this schema, and affect that exact linked scope.
Factory and resume MUST resolve to distinct local callable declarations with
complete shapes; `handleType` MUST resolve to a local type declaration.

Every endpoint is compared through its full CSMI identity and artifact scope.
Display names, source spelling, rendered signatures, and producer-local handles
are never substitutes. The linked scope describes eligible endpoint semantics;
it does not assert that a particular factory result reaches a particular resume
invocation. A consumer MUST independently prove that concrete value flow,
including any supported alias or adaptation, before applying a yield. Matching
handle type alone is insufficient.

## Construction and deferred events

`construction.source` identifies an input boundary on `factory`.
`construction.handle` identifies its output handle. Construction establishes a
source-to-handle retention relationship; it is not a core transfer, is not a
yield, and does not eagerly move source entries into caller state.

The resume record separately identifies the input handle and normal item result
on `resume`. A yield may occur only at that later resume boundary after the
consumer has established the handle-flow proof above. `perResume` is exactly
`zero-or-one`; `perHandle` is exactly `zero-or-more`. The contract does not
assert invocation, termination, exhaustion, order, monotonic progress, exact
count, or a must-yield edge. A consumer MUST preserve the zero-yield path and
MUST NOT rewrite a deferred yield as an eager factory-call transfer.

## Source shape, members, and delivery

Root shapes and projections describe portable logical observations rather than
compiler storage. A keyed source has explicit key and value shapes. A yield
member selects a source observation through an ordered projection and binds it
to one zero-based item position. `role: "key"` and `role: "value"` preserve an
explicit entry decomposition; `role: "item"` covers a non-entry source.
Positions, roles, and projections MUST be unique and in range for the yielded
product shape. Tuple size, component spelling, property order, destructuring
syntax, or names do not establish key/value correspondence.

Delivery is separately `shared-borrow`, `exclusive-borrow`, `move`, `copy`, or
`derived`. It is never inferred from retention. Shared-borrow delivery does not
permit mutation; exclusive-borrow delivery preserves exclusive access but not
ownership; move transfers the modeled value; copy separates the delivered
value from source storage; derived admits information influence without exact
preservation. Unsupported or unknown delivery carries a typed limitation and
cannot support complete coverage.

## Retention, validity, and invalidation

`borrowed-shared`, `borrowed-exclusive`, and `owned` retention describe the
source-to-handle relation. They are semantic access modes, not source-language
spellings. Shared retention cannot justify exclusive delivery; borrowed
retention cannot justify move delivery; those stronger claims require separate
supported evidence.

Validity records whether yields remain tied to the source or handle and has
explicit unknown and unsupported forms. Invalidation may name source mutation
or handle drop, may explicitly assert nothing, or may remain typed as unknown
or unsupported. `none-asserted` means the profile asserts no portable
invalidation event; it is not proof of permanent validity or absence of
language-specific lifetime constraints. Unknown or unsupported relevant state
prevents complete profile coverage.

## Equality, conflict, merge, and completeness

Equality compares exact vocabulary version, family, linked scope, endpoint
roots and shapes, retention, validity and invalidation, multiplicity, ordered
item positions, source projections, and delivery after core identity
comparison. Exact duplicates add no evidence. Non-equivalent candidates remain
alternatives or conflicts; input order never selects truth. A consumer MAY
union compatible positive may-yield evidence but MUST NOT merge incompatible
identity, shape, retention, mapping, or validity into one exact contract.

`deferred-yields` completeness closes only the exact
factory/resume/handle-type relation. It does not close dispatch,
consumer-local handle-flow proof, termination, exhaustion, order, concrete
count, mutation, exceptions, cleanup, core procedure summaries, or another
fact family. Unknown or unsupported semantics, unresolved identity, incomplete
declaration evidence, conflicts, cancellation, budget exhaustion, stale inputs,
or unavailable dependencies prohibit `complete`. Partial statements carry core
typed limitations; omission and empty arrays remain open-world.

Consumers lacking this exact required vocabulary treat the affected linked
scope as uninterpretable. They MUST NOT drop the event, flatten it to a root,
accept a nearby version, approximate it as a during-call transfer, or cache an
incomplete result as reusable-complete.

## Versioning and evidence

Version `0.1.0` introduces this vocabulary. Existing documents require no
migration. New producers opt in, and consumers implement this exact version or
fail closed.

Rust's [`HashMap::iter`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.iter)
and [`Iterator::next`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#tymethod.next)
provide motivating ecosystem evidence: construction returns a handle, and
later calls may return successive items. Shared, mutable, and owned
`IntoIterator` forms motivate distinct retention and delivery modes, but Rust
names, `Option`, trait dispatch, loop desugaring, and tuple spelling are not
portable facts. The fixtures and independent consumer exercise are reference
evidence, not production-adapter certification.
