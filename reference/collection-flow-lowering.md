# Collection-flow consumer integration

This guidance accompanies `csmi.collection-flow` `0.1.0`; the normative wire
contract is in `profiles/collection-flow/0.1/profile.md`. It describes importer
obligations, not implemented Bifrost support.

## Applicability and identity

1. Dispatch on the exact profile identifier, version, and schema. Validate the
   core document and profile payload, then cross-record semantic invariants.
2. Retain provenance and each exact affected family/scope. Require matched
   artifact applicability and resolver-proven callable and type identity before
   applying facts. Preserve multiple candidates and indeterminate outcomes.
3. Resolve declaration parameter positions from the callable shape. Never use
   argument source order, display names, rendered signatures, or producer handles
   as a replacement for semantic identity.

## Structured substitution

Build a substitution environment from the exact generic declaration's ordered
parameters and the instantiated receiver's ordered structured arguments. Apply
it recursively to core reference arguments and parameter references. Keep the
symbol's artifact scope. Do not stringify types, erase arguments, infer an
inheritance substitution from an owner name, or equate unknown types. A raw,
partially resolved, variant, higher-kinded, or otherwise unrepresentable input
must retain its limitation rather than become an exact binding.

## Invocation and memory boundaries

Lower keyed projections into the consumer's own abstract collection locations.
A parameter-selected key denotes the runtime argument value under the resolved
collection semantics; it is not that parameter's spelling. Aggregate entry
selection denotes an abstract set and does not prove non-emptiness, iteration
order, uniqueness of a callback execution, or a strong update.

Create a distinct callback invocation boundary and bind profile argument
transfers to its canonical parameter positions. Resolve callback targets using
consumer analysis; a transferred function value does not prove one target. Do
not model a callback input as caller-visible output state of the enclosing
procedure. Preserve zero or more invocations and all unresolved alternatives.

Apply product component projections only with explicit supported product
semantics. Map component positions into consumer-local bindings using resolver
or compiler evidence for the actual destructuring operation. Those local
binding IDs stay in the consumer. A Java entry getter, Scala product component,
or C# deconstructor must not become equivalent merely because names or source
syntax resemble a key/value pair.

## Completeness and migration

Profile family coverage, core procedure-summary coverage, callback target
coverage, and consumer analysis termination are independent. Missing support,
budget exhaustion, cancellation, ambiguity, or failed mapping must not yield a
complete empty summary. Retain positive facts only where they remain sound and
report affected units as partial, unknown, unsupported, or uninterpretable as
appropriate. No fact here licenses must-flow, alias identity, exact values,
strong updates, exception exclusion, or taint preservation by itself.

Old documents require no migration: the core schema remains `0.1-json` and the
semantic model remains `0.1`. Producers opt in with the exact required profile
use and affected units. Consumers must explicitly implement `0.1.0`; accepting
or round-tripping its JSON is not semantic support. A weaker core projection is
permitted only when sound and separately covered; dropping an unsupported path
or callback boundary is not a migration strategy.

## Suggested Bifrost implementation boundary

Keep wire decoding and semantic validation separate from call-site lowering.
Represent profile endpoints, type substitutions, callback argument positions,
and coverage outcomes with typed structures. Import the exact vocabulary as a
capability; unsupported variants should return a typed result carrying the
original affected scope and provenance.

At lowering time, resolve the instantiated receiver and callable first. Apply
ordered substitution to the imported structured types, then lower the supported
projections through the existing memory abstraction. Dispatch callback facts
through the existing call-target and parameter-binding machinery. Bind product
components through semantic destructuring evidence, retaining component indices
until they reach consumer-local values. This is an integration plan, not a
requirement to share Bifrost classes or heap identifiers on the wire.

Before declaring support, add importer round trips and malformed-wire tests,
then end-to-end positives and near misses for exact generic receivers, unrelated
same-named types, nested arguments, unknown receiver arguments, callback target
ambiguity, incorrect arity, non-product entries, and interrupted analysis. Verify
that an unsupported profile cannot enter a reusable complete summary cache.
