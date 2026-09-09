# CSMI collection-flow profile 0.1.0

This normative document assigns `csmi.collection-flow` exact version `0.1.0`
and schema `https://csmi.brokk.ai/schema/profiles/collection-flow/0.1/schema.json`.
It is a new standard vocabulary under core section 3.6, not a core extension
that silently changes `0.1` or `0.1-json`. Its only dependency is CSMI core
`0.1` serialized as `0.1-json`; identity schemes retain their own dependencies.

## Attachment, identity, and applicability

A payload is one `extensionFacts[]` record with `vocabulary` equal to
`csmi.collection-flow`, `version` equal to `0.1.0`, family `collection-flows`,
and exact scope `{ "callable": <local symbol reference> }`. Its payload
`callable` MUST equal that scope. The vocabulary use MUST be `required`, name
the exact schema, and list this family and scope in `affects`. There are no
other attachment points in this version. Projection syntax is reused inside
these facts; this version does not authorize attaching its paths directly to a
core transfer without the profile's root-shape context.

The referenced callable MUST resolve to a local callable declaration with its
complete callable shape. Local symbol references are document indirections to
core structured identity, not producer-local identity. Cross-document matching
MUST use the referenced symbol's full identity and artifact scope. Declaration,
identity-scheme, artifact selector, compatibility, and provenance requirements
remain those of core. Every applied fact MUST have matched artifact
applicability and supported exact identity evidence. Missing or indeterminate
evidence prevents application; a matching name is never a substitute.

## Wire payload and root shapes

A payload has `kind: "collection-flow"`, `callable`, `roots`, `transfers`, and
`invocations`, with optional `receiverSubstitution`. Arrays of transfers and
invocations are unordered sets. Root descriptions are a map keyed by exact core
boundary root; duplicate roots are invalid. Every used boundary root MUST have
one shape and MUST exist in the enclosing callable shape. `roots` describe
portable observations, not compiler storage or physical layouts.

Shapes are recursive:

- `{ "kind": "value", "type": <core type expression> }`;
- `{ "kind": "product", "components": [<shape>, ...] }`, a nonempty ordered
  product with zero-based component positions;
- `{ "kind": "keyed", "key": <shape>, "value": <shape> }`, optionally with
  `entryComponents: ["key", "value"]` or `["value", "key"]`;
- `{ "kind": "unknown", "limitation": <core typed limitation> }`.

A keyed shape asserts an abstract association between key and value. It does
not select an equality implementation, imply unique concrete storage, or prove
absence of colliding keys. `entryComponents` is explicit evidence that an entry
admits the stated ordered product observation. Absence means no such mapping
is asserted. Java entries, arbitrary extractors, and C# deconstructors MUST NOT
receive a product mapping from their names. Producers need semantic evidence
for each claimed mapping. Product shape is a profile observation, not a new
core type-expression kind; leaf types retain the existing recursive core wire
shape, identity, ordered arguments, and unknown values.

## Receiver substitution

`receiverSubstitution: { "kind": "receiver-arguments", "declaration": <type> }`
defines a substitution recipe. The type MUST be a local generic type declaration
with a complete ordered sequence of type parameters, each owned by that type.
The enclosing callable's receiver type MUST reference that exact declaration
with its parameters in declaration order. No receiver, a different owner,
non-type generic parameter, or missing argument is invalid for this recipe.

At a call site the consumer MUST obtain an instantiated receiver reference to
that exact type. Bind each declaration parameter to its corresponding ordered
structured argument, then recursively substitute parameter references in
profile shapes. A nested reference remains nested. A concrete argument can
itself contain supported symbolic parameters; unresolved/unknown arguments
remain unknown. A raw receiver, missing arguments, ambiguous instantiation, or
unresolved identity MUST NOT produce an exact substitution. An inherited view
requires separate resolver-proven evidence before it can be used as this exact
receiver; this profile does not infer subtyping, variance, alias expansion,
wildcards, higher-kinded application, or language-specific adaptation.

A producer can instead encode `kind: "unknown"` or `"unsupported"`, each with
`limitation`. Such a recipe cannot close a complete profile scope. Missing
`receiverSubstitution` asserts no recipe; it does not erase generic arguments.

## Projection algebra

Locations reuse core `root` and optional `projection`. A projection has
`scheme: "csmi.collection-flow"`, `schemeVersion: "0.1.0"`, and ordered `steps`:

```json
{"kind":"entry","args":{"key":{"kind":"parameter","position":0}}}
{"kind":"entry","args":{"key":{"kind":"all"}}}
{"kind":"entry-key"}
{"kind":"entry-value"}
{"kind":"component","args":{"position":1}}
```

`entry` accepts only a keyed shape and selects an abstract set of entries.
`all` includes zero or more entries. A parameter selector uses the runtime
value bound to the enclosing callable's input parameter at that canonical
position, including when the collection root is output-phase. It does not name
a key by spelling, imply key existence, or make two different parameter
positions disjoint. `entry-key` and `entry-value` accept only entry results.
`component` accepts a product or an entry with explicit `entryComponents`, and
its position MUST be in range. Subsequent projections apply pointwise through
an entry set; nested keyed/product shapes compose in the same way. No projection
through an unknown shape is interpretable.

Equality requires equal core roots and equal ordered structured steps after
identity comparison. `entry(all)` covers each parameter-selected entry at the
same prefix. Different parameter selectors may overlap; even different input
values do not prove key disjointness without supported collection equality.
Different entry members or product components denote distinct observations,
not necessarily disjoint storage or independent information. Beyond identical
paths and this wildcard rule, this version provides no subsumption proof.
Consumers MUST preserve uncertainty rather than infer disjointness or discard
paths. Unknown types never become equal merely because their JSON is equal.

## Enclosing transfers

`transfers` uses `{ "source": <input location>, "destination": <output location> }`.
Its meaning is core directional may-information transfer applied to the
profile's supported locations. For example the update payload in
`fixtures/valid/update.json` states:

`parameter[1] -> output receiver.entry(input parameter[0]).entry-value`.

This does not assert mutation success, must-flow, value preservation, aliasing,
strong update, key insertion, exception exclusion, or taint preservation.
Unprojected output parameter writeback is unsupported in this profile version;
other profiles can define it separately. Transfers may select a product
component at input and expose its information in an output logical result,
as `fixtures/valid/product-component.json` demonstrates. Consumer-local
bindings are established by consumer resolver/compiler evidence and are not
serialized as portable symbols by this profile.

## Higher-order invocation boundary

An invocation contains `callback` (an enclosing input location), `parameters`
(an ordered array of callback input shapes), `arguments` (an unordered set of
`{ "source": <enclosing input location>, "parameter": <zero-based position> }`),
and `timing: "during-call"`. It asserts a possible invocation of the callback
value during the enclosing invocation, with structural may-information transfer
to the given callback parameter. It does not identify a unique callback target,
guarantee execution, order, count, or termination, or describe deferred calls.
A consumer MUST resolve actual targets and validate their canonical parameter
shape; unresolved alternatives remain observable. Callback results, exceptions,
receiver adaptation, deferred execution, and post-mutation iteration are not
expressible by this version's input-only callback sources.

Structural argument transfer applies recursively to corresponding leaf
observations: product component i may influence callback component i. Keyed
entry-to-product transfer requires `entryComponents`; keyed key/value layout
and leaf structured types must agree. Unknown layouts remain uninterpretable
for this structural correspondence. This is stronger than an unstructured
whole-value may-information edge but does not imply exact values or aliases.
A producer MUST NOT attach it to arbitrary transforming callbacks or use it to
invent component correspondence. Transfers to a callback parameter are not
output parameter writes of the enclosing call.

`fixtures/valid/entry-callback.json` supplies an entry as callback parameter 0
with key/value components. `two-argument-callback.json` supplies key and value
to parameters 0 and 1 separately. This distinction supports materially different
APIs without imposing tuple calling conventions on every language.

## Equality, conflict, merge, and completeness

A record is a contract candidate for one exact callable scope. Equality
compares exact vocabulary version, family, scope, substitution, root shapes,
and transfer/invocation sets after core identity comparison. Product components
and callback parameters are ordered; roots and transfer/argument/invocation
sets are not. Exact equivalent duplicates add no evidence. Non-equivalent
candidates remain alternatives/conflicts, not an input-order winner. A consumer
MAY conservatively union independently interpretable positive may-flow evidence
but MUST NOT merge incompatible root shapes or recipes into one exact contract.
Unknown identities/layouts prevent equivalence proofs.

`collection-flows` completeness is scoped by exactly `{ "callable": <symbol> }`.
Complete closes the set of modeled enclosing and during-call callback transfers
under this profile; it does not close core procedure summaries, callback target
resolution, heap mutation, exceptions, or other effects. Conflicting candidates,
unknown/unsupported shapes or substitution, incomplete required declarations,
unsupported relevant behavior, cancellation, budget exhaustion, stale inputs,
or unavailable dependencies prohibit complete coverage. Partial statements
carry core typed limitations; omission remains open-world. Empty arrays do not
imply completeness. A complete empty scope is meaningful only when all core
applicability, support, evidence, and coverage obligations have been met.

Consumers lacking this exact required vocabulary treat affected units as
uninterpretable. They MUST NOT drop a projection, substitute display text,
flatten generic types, reuse a callback as a core output, or cache an incomplete
result as complete. A weaker core projection is permitted only when separately
sound and separately covered.

## Evidence and version history

Version `0.1.0` introduces this vocabulary; core versions are unchanged. There
is no migration of existing documents. New producers opt in through exact
required uses; consumers must explicitly implement the new semantics.

The payload and full-document fixtures are manually authored portable
conformance producers with reserved example identities. The independent token-set
consumer and structural substitution exercise in
`scripts/validate-collection-flow.py` implement the exchanged algebra without
Bifrost data structures. They are reference evidence, not compiler adapter or
production interoperability certification. The Java two-argument and
Scala/Kotlin entry-product cases intentionally retain different invocation
shapes. See `reference/collection-flow-ecosystems.md` for primary API evidence,
retained/erased/unsupported distinctions, and near misses. C# deconstruction is
mapping evidence, not an implemented adapter.
