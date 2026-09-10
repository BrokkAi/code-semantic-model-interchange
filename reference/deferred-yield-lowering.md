# Deferred-yield consumer integration

This guidance accompanies `csmi.deferred-yield` `0.1.0`; the normative wire
contract is in `profiles/deferred-yield/0.1/profile.md`. It describes importer
obligations. The Rust section is motivating ecosystem evidence and a lowering
sketch, not a normative API requirement or an implemented Bifrost adapter.

## Applicability and identity

1. Dispatch on the exact profile identifier, version, and schema. Validate the
   core document, profile payload, and the exact linked
   factory/resume/handle-type scope
   before applying facts.
2. Require resolver-proven identities and matched artifact applicability for
   both endpoints. Preserve alternatives when either endpoint can dispatch to
   more than one implementation.
3. Establish a consumer-local handle identity at a supported construction. Do
   not use the factory or resume display name, source spelling, object identity
   layout, producer handle, or position in a document as portable identity.

## Handle, source, and event lowering

Represent the handle, its retained collection source, retention, validity,
invalidation, delivery, and completeness as distinct typed facts. Construction
creates or establishes the handle and source relation. A resume is a separate
event on that handle and delivers at most one item per call. Preserve the loop
or repeated-call semantics already represented by consumer control flow,
including the zero-iteration path; do not fabricate a loop or strengthen the
contract to exactly one, at least one, ordered, or finite.

Lower an entry only through its explicit key/value member mapping. Bind
delivery to the consumer's own borrow, move, copy, and derived-value machinery.
Keep the collection source separate from the delivered item and separate items
from each other. Borrowed-shared, borrowed-exclusive, and owned retention are
different states;
a borrow spelling or constructor name cannot promote one to another.

Treat the validity record as a precondition on continuing interpretation and
its invalidation record as a conservative kill or uncertainty event. When the
consumer cannot prove that a constraint holds, preserve partial or unknown
coverage with its limitation. An absent constraint set is open-world, not
proof of permanent validity.

## Completeness and cache safety

Profile-family coverage is independent of endpoint target resolution, concrete
collection behavior, exception behavior, cleanup, consumer termination, and
procedure-summary coverage. Ambiguity, cancellation, budget exhaustion, missing
identity, failed substitution, unproven member mapping, and unsupported
retention, delivery, or invalidation prohibit a complete profile result. Do not
cache such a result as complete or reusable-complete. A weaker eager projection
may be separately useful only when independently sound and independently
covered; it is not a lowering of this profile.

Before claiming support, test exact linked endpoints, unrelated same-named
endpoints, missing endpoints, zero-iteration and repeated-resume paths, explicit
and unproven entry mappings, all retention and delivery variants, recorded and
unrecorded invalidation, conflicts, partial evidence, unsupported versions, and
interrupted analysis. Include a positive where a factory handle is resumed and a
near miss where an unrelated handle of the same type is resumed.

## Non-normative Rust evidence

Rust's standard library demonstrates the model rather than defining it.
[`HashMap::iter`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#method.iter)
constructs an iterator that borrows the map; iteration through `&HashMap` uses
[`IntoIterator`](https://doc.rust-lang.org/std/collections/struct.HashMap.html#implementations);
`HashMap::iter_mut` constructs a mutable iterator; and `HashMap::into_iter` can
consume ownership depending on the instantiated receiver. The resulting
handles are consumed by later repeated
[`Iterator::next`](https://doc.rust-lang.org/std/iter/trait.Iterator.html#tymethod.next)
calls. The standard documentation describes `next` as advancing
the iterator and returning an `Option`: `Some` wraps the next item when present,
and `None` reports exhaustion.

Those APIs motivate the separation of factory, handle, collection source,
resume, zero-or-one-per-call/zero-or-more-per-handle multiplicity, key and value
entry members, retention, and invalidation. Rust `Option` desugaring,
`for`-loop adaptation, hash randomization, concurrent mutation rules, allocator
behavior, and implicit drops are not represented by this profile. A Rust
producer must provide resolver-proven identities for the exact construction and
resume callables and must preserve unsupported cases such as ambiguous trait
dispatch, unproven key/value component order, collection mutation during a
shared iterator, and unmodeled cleanup as typed incompleteness.
