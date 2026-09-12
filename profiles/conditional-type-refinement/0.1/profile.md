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

`semantics: "biconditional"` means a truthy result refines the subject to the
target and a false result excludes the target from the subject. This is the
portable meaning needed for Python `TypeIs`. `semantics: "positive-only"`
means only the truthy refinement is asserted; the false branch carries no
negative refinement. This is the portable meaning needed for Python
`TypeGuard`. Neither value identifies a runtime test implementation, promises
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
subject, vocabulary, artifact, and target identities match. On a truthy branch
both semantic modes add the target. On a false branch only `biconditional`
excludes it; `positive-only` leaves the input type information unchanged. A
closed failure, a conflict, an unknown required vocabulary, or uninterpretable
identity yields an uninterpretable refinement result rather than empty facts.

## Evidence and version history

Version `0.1.0` introduces the vocabulary without changing CSMI core. The
fixtures are manually authored conformance producers. The independent branch
consumer in `scripts/validate-conditional-type-refinement.py` consumes only the
wire contract and demonstrates the distinct false-branch behavior plus
fail-closed handling. It is interoperability evidence, not a Bifrost adapter or
production certification.
