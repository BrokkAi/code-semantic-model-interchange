# CSMI conditional-type-refinement profile 0.1.0

This normative document assigns `csmi.conditional-type-refinement` exact
version `0.1.0` and schema
`https://csmi.brokk.ai/schema/profiles/conditional-type-refinement/0.1/schema.json`.
It is an independently versioned semantic profile over CSMI core `0.1`; it does
not add a source-language feature or type form to core.

## Attachment and identity

One payload is carried by an `extensionFacts[]` record with family
`conditional-type-refinements`. Its exact scope is
`{"callable": <local symbol reference>, "subject": {"kind":"parameter", "position":N}}`.
The payload `callable` and `subject` MUST equal that scope. The vocabulary use
MUST be `required`, name the exact schema above, and list the exact family and
scope in `affects`.

`callable` MUST resolve to one local declaration whose category is `callable`
and whose complete callable shape contains the zero-based canonical parameter
ordinal in `subject.position`. This is an exact callable identity through the
core symbol table and its artifact scope, not a name or rendered signature.
Overload members therefore have distinct callable symbols. Display names,
producer-local IDs, parameter labels, and source offsets MUST NOT substitute
for this identity.

## Outcomes and target types

Every applicable scope records exactly one `outcome`. A supported outcome is:

```json
{
  "kind": "supported",
  "semantics": "biconditional",
  "target": {"kind":"reference", "symbol":"Sequence", "arguments":[{"kind":"reference", "symbol":"Text"}]}
}
```

`target` reuses the core structured type-expression shapes: exact local
`reference` identity with recursive ordered arguments, local generic
`parameter` identity, or a versioned `intrinsic`. `unknown` is intentionally
not a supported target. Every referenced symbol MUST resolve to the appropriate
local type or type-parameter declaration; a consumer MUST NOT repair missing
identity using spelling, source text, or a rendered type.
Every intrinsic target MUST have an exact required vocabulary use for its
identifier and version; an undeclared, optional, or unsupported intrinsic makes
the refinement uninterpretable.

`semantics: "biconditional"` means a true result intersects the subject with the
target and a false result excludes the target from the subject. This is the
portable meaning needed for Python `TypeIs`. `semantics: "positive-only"`
means the true branch takes the target type as its refined type; the false
branch carries no negative refinement. Unlike biconditional intersection, this
positive replacement does not require the target to be a subtype of the incoming
type (for example, invariant `list[object]` to `list[str]`). This is the portable
meaning needed for Python `TypeGuard`. Neither value identifies a runtime test implementation, promises
purity, nor establishes subtype compatibility outside separately available
type-system evidence.

An unsupported or indeterminate outcome contains a typed `limitation` and no
target or semantics. `unsupported-target`, `conflicting-overloads`, and
`uninterpretable-semantics` are explicit fail-closed results. Producers MUST
emit one of these outcomes when the applicable callable was examined but no
sound supported fact can be produced. They MUST NOT emit a supported fact with
an unknown target, choose an overload by input order, flatten a target to text,
or turn failure into an empty fact set.

## Conflict, merge, completeness, and consumption

Equality compares exact vocabulary version, family, scope, and the complete
payload after core identity comparison. Equivalent duplicates add no evidence.
Non-equivalent outcomes for one exact scope are a conflict. In particular,
different target types, different semantics, or a supported outcome alongside
a closed failure MUST remain conflicting alternatives; consumers MUST NOT pick
one, intersect them, or union them into a stronger refinement.

Completeness uses family `conditional-type-refinements` and the exact callable
and subject scope. `complete` means the producer considered all portable
conditional-refinement semantics for that subject. Conflicting candidates,
unsupported or indeterminate outcomes, incomplete callable shape, unresolved
target identity, unsupported relevant behavior, cancellation, or stale inputs
prohibit complete coverage. Partial coverage retains core limitations.
Omission remains open-world and never means “no refinement.”

An independent consumer applies a supported fact only after exact callable,
subject, vocabulary, artifact, and target identities match. On a true branch
`biconditional` intersects the incoming type with the target; `positive-only`
replaces the incoming type with the target. On a false branch only `biconditional`
excludes it; `positive-only` leaves the input type information unchanged. A
closed failure, a conflict, an unknown required vocabulary, or uninterpretable
identity yields an uninterpretable refinement result rather than empty facts.

## Invocation and overload agreement

Version 0.1.0 applies to a normal Boolean result of a callable with exactly one
logical result at position zero. A producer or consumer MUST establish that
Boolean result contract through trusted semantic evidence; arbitrary truthiness
conversions and exceptional returns are outside this profile. The subject is
the bound parameter value at the result observation; transporting the fact back
to a caller expression requires proof that the expression still denotes that
value. The fact does not prove absence of mutation or alias invalidation.

A resolved single callable may use its exact scope. If dispatch leaves multiple
applicable overloads, the consumer MUST enumerate the complete candidate set,
bind each subject ordinal to the same caller value, instantiate type parameters,
and compare the resulting semantics and structured target identities. Every
candidate MUST supply an interpretable supported fact and agree; missing,
unsupported, or conflicting candidates prohibit narrowing. A partial candidate
set cannot establish agreement. Distinct overload symbols do not compare equal
merely because their display names match. Equivalent repeated facts for one
scope are deduplicated before this comparison. This profile carries facts for
individual callable symbols, not an overload-resolution algorithm.

Unbound or out-of-scope type parameters, unknown generic argument semantics,
unresolved aliases, and unsupported structural predicates are uninterpretable.
The structural shape alone does not certify that a consumer can interpret a
target; generic arguments MUST NOT be erased to a nominal class test.

## Evidence and version history

Version `0.1.0` introduces the vocabulary without changing CSMI core. The
fixtures are manually authored conformance producers. The independent branch
consumer in `scripts/validate-conditional-type-refinement.py` consumes only the
wire contract and demonstrates the distinct false-branch behavior plus
fail-closed handling. It is interoperability evidence, not a Bifrost adapter or
production certification.

The motivating semantics are checked against the [Python typing specification's
TypeGuard and TypeIs rules](https://typing.python.org/en/latest/spec/narrowing.html).
The fixtures exercise a language-neutral projection, not a generated Python
producer or an independent production implementation. Other language mappings
require their own identity, invocation, and type-system evidence.
