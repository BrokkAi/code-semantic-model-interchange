# JavaScript, TypeScript, and Node profile family 0.1

Status: **normative standard profile**.

This profile family defines the portable identity and applicability rules needed
to bind CSMI facts to ECMAScript runtime bindings, TypeScript declaration
bindings, Node builtins, and npm packages. It supplements the CSMI 0.1 core; it
does not add properties to core objects or standardize an analyzer's module
graph, type checker, or semantic-pack representation.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**,
and **MAY** are to be interpreted as described by BCP 14 when, and only when,
they appear in all capitals.

## 1. Profile identities

This family assigns two independently supported standard vocabularies:

| Identifier | Version | Schema | Purpose |
| --- | --- | --- | --- |
| `csmi.javascript-typescript` | `0.1.0` | `https://csmi.brokk.ai/schema/profiles/javascript-typescript/0.1/schema.json` | Runtime and declaration identity, binding evidence, and runtime-to-declaration mappings. |
| `csmi.node-compatibility` | `0.1.0` | `https://csmi.brokk.ai/schema/profiles/node-compatibility/0.1/schema.json` | Node runtime, module-resolution, package-condition, TypeScript-resolution, and project-configuration compatibility. |

The exact strings above are opaque profile versions under CSMI section 3.6.
Supporting another version, or merely validating one of these schemas, does not
establish support for `0.1.0`.

Every use of either vocabulary in this profile family affects identity,
binding, artifact applicability, compatibility, completeness, or a core fact.
It therefore MUST be declared `required` and MUST name the affected core slot,
attachment, fact family, or completeness claim. Removable presentation
metadata uses core display fields or a separate optional vocabulary; these two
vocabulary identifiers are never declared `optional`.

## 2. Artifact roles and applicability

Artifact identity remains a CSMI core PURL selector. This profile does not mint
a second package identity syntax.

| Modeled artifact | Canonical selector form | Meaning |
| --- | --- | --- |
| npm runtime package | Registered npm PURL, for example `pkg:npm/example@4.2.0` | Runtime implementation distributed by npm. |
| scoped npm runtime package | Percent-encoded registered npm PURL, for example `pkg:npm/%40scope/example@4.2.0` | Runtime implementation distributed by npm. |
| separate declarations | Their own npm PURL, for example `pkg:npm/%40types/node@22.10.2` | Declaration artifact only; it is not the Node runtime and does not inherit runtime completeness. |
| Node distribution | `pkg:generic/nodejs.org/node@<exact-version>` plus an archive digest | The exact official Node runtime distribution whose builtin registry and behavior are modeled. |

The Node generic PURL name and namespace above are assigned by this profile;
case variants and alternate names are not aliases. Because the registered
generic PURL type provides no Node naming authority, every Node distribution
selector MUST also contain a digest over one identified official distribution
archive, with coverage `official-distribution-archive`. The selector therefore
identifies both the release coordinate and exact distribution bytes. A
version-range selector for a Node distribution is not portable in this profile
because the core requires a VERS type applicable to the selector PURL type and
the current VERS registry defines no generic or Node type. Producers MUST use an
exact Node distribution selector, or exact alternatives, rather than inventing
Node VERS semantics.

An npm package's bundled declarations share its artifact scope only when those
declarations are bytes of the selected package. Declarations from another
package, including `@types/*`, MUST carry their own `artifactSelectors` on their
symbol definitions. A `runtime-declaration-binding` fact relates those symbols;
it does not merge their identities, provenance, applicability, or completeness.

Artifact matching is evaluated before compatibility. A missing candidate
package version, unknown PURL equivalence, unavailable required digest, or
unresolved conditional export produces core `indeterminate` applicability. It
MUST NOT be repaired from an import spelling, source text, a lockfile display
name, or the presence of a similarly named declaration package.

## 3. JavaScript runtime identity scheme

The identity scheme `csmi.javascript-runtime` at scheme version `0.1.0` names
resolver-proven runtime bindings. Its stability is `portable` only for an
artifact-visible builtin or package export established by the applicable
runtime resolver. File-local, eval-created, dynamically computed, anonymous,
and unresolved properties are not portable identities.

The descriptor path begins with exactly one `namespace` descriptor:

- a Node builtin uses the canonical registry key `node:<builtin-id>`, such as
  `node:child_process`; or
- an npm package export uses the canonical package export key selected after
  package resolution: `.` for the root or the exact `./subpath` key parsed from
  the selected artifact's `exports` map.

Package export keys are compared as exact Unicode scalar-value sequences. The
profile performs no filesystem path normalization, percent decoding, Unicode
normalization, slash folding, dot-segment removal, or case folding. Invalid or
unresolved export-map keys do not produce portable identity.

This descriptor is not raw module-string identity. The artifact PURL and
resolver evidence establish the package or builtin registry; the scheme then
constructs the canonical key. Relative paths, absolute paths, source text,
unresolved bare strings, and producer display names MUST NOT be substituted.

Subsequent descriptors follow these rules:

- a named exported value uses `term`;
- an invocation target uses `callable`, with a scheme-defined disambiguator
  only when distinct resolver-visible callable bindings would otherwise
  collide;
- a runtime constructor or class uses `type` for the constructable binding. A
  nested member MUST include a following `meta` descriptor named exactly
  `static` or `prototype` before the member descriptor, so same-named members
  on the two receivers cannot collide;
- a CommonJS `module.exports` binding uses the normalized name `default`; and
- an unnamed or computed export without a stable resolver key is omitted from
  portable identity and limits any covering completeness claim.

ECMAScript has no overload identity at runtime. Type annotations, TypeScript
overload signatures, source order, arity observations, and inferred types MUST
NOT disambiguate a JavaScript runtime binding.

### 3.1 CommonJS and ESM bindings

CommonJS and ESM syntax are binding forms, not automatic symbol identities.
Two forms denote the same runtime symbol only when the applicable resolver and
artifact prove that they select the same exported binding.

For a Node builtin that permits both forms, `require("child_process").execSync`
and the ESM named import from `node:child_process` resolve to the same symbol
whose module descriptor is `node:child_process`. The bare and `node:` spellings
are accepted aliases only for builtin identifiers that the selected exact Node
distribution exposes without a mandatory prefix. A builtin that Node exposes
only with a mandatory `node:` prefix has no bare alias. A same-spelled npm
package is never an alias for a builtin.

For npm packages, `import`, `require`, `default`, `node`, `types`, custom
conditions, the package `type`, and the selected export key may resolve to
different files or bindings. Equality is established after resolution, not
from equal specifier text. If `import` and `require` select different exports,
the producer MUST use distinct semantic models or symbols with compatibility
constraints that separate the variants. A default import from CommonJS binds
the normalized `module.exports`/`default` binding; it does not by itself alias
every named property.

A `module-binding` attachment records auditable resolver evidence. Its
`canonicalModule` and `exportName` MUST agree with the attached symbol's
descriptor path. `acceptedSpecifiers` is a set of proven spellings for the
selected artifact and compatibility context; it is never an identity fallback.
Each entry's `value` is exactly one source-level module specifier (for example
`child_process` or `node:child_process`), while `form` identifies the binding
form. The payload-level `exportName` identifies the first exported descriptor.
The value does not embed the export name, property path, quoting syntax, or
source location.

## 4. TypeScript declaration identity scheme

The identity scheme `csmi.typescript-declaration` at scheme version `0.1.0`
names declarations established by a TypeScript-compatible resolver. JavaScript,
TypeScript, TSX, declaration files, and generated declarations may all refer to
the same runtime binding while retaining separate declaration identities.

The first descriptor uses the same canonical builtin or package-export key as
section 3, but under this distinct scheme. The remaining path preserves
TypeScript declaration spaces:

- namespace/module declarations use `namespace`;
- type-space declarations use `type`;
- value-space non-callables use `term`; and
- call, construct, getter, and setter signatures use `callable`.

Same-spelled declarations in distinct spaces are distinct. Static and instance
members use the same mandatory `meta` receiver descriptor defined in section
3. Declaration merging does not collapse type and value identities. A callable
overload uses a `tsig-0.1:<digest>` disambiguator, where `digest` is unpadded
base64url SHA-256 over an RFC 8785 JSON Canonicalization Scheme record with
exactly these members:
`callableKind` (one of `call`, `construct`, `getter`, or `setter`),
`typeParameterCount` (non-negative integer), `receiver` (a canonical type or
JSON `null`), `parameters` (ordered records containing `binding`, `required`,
`rest`, and canonical `type`), and canonical `result` type. `binding` is one of
`positional-only`, `named-only`, or `positional-or-named`; both booleans are
always present. A canonical type is one of these closed tagged records:

- `{ "kind": "intrinsic", "name": <ECMAScript intrinsic> }`;
- `{ "kind": "reference", "artifactSelectors": <canonical core selector set>,
  "scheme": <scheme>, "schemeVersion": <version>, "stability": <class>,
  "descriptors": <canonical descriptor sequence> }`;
- `{ "kind": "array", "element": <type> }`;
- `{ "kind": "tuple", "elements": [<type>...] }`;
- `{ "kind": "union"|"intersection", "members": [<type>...] }`;
- `{ "kind": "function", "signature": <this exact signature record> }`;
- `{ "kind": "literal", "value": <JSON string, number, or boolean> }`;
- `{ "kind": "keyof", "operand": <type> }`;
- `{ "kind": "indexed", "object": <type>, "index": <type> }`; or
- `{ "kind": "type-parameter", "position": <non-negative integer> }`.

Intrinsic names are exactly `any`, `bigint`, `boolean`, `never`, `null`,
`number`, `object`, `string`, `symbol`, `undefined`, `unknown`, and `void`.
Object keys are JCS ordered; union and intersection members are sorted by their
canonical bytes and deduplicated; tuple and parameter order is retained;
aliases remain resolver-proven reference identities and are not expanded.
Every reference embeds its complete CSMI symbol identity rather than a
document-local handle.

Source order, overload ordinal, pretty-printed display text, erased arity alone,
and source offsets are forbidden portable disambiguators. If a producer cannot
construct the closed canonical type tree, the overload has no portable identity
and limits completeness. If a consumer cannot implement `tsig-0.1`, identity
comparison is indeterminate.

Generated `.d.ts` output and ambient modules use the same construction only
when the producer resolves them to an exact declaration artifact. `origin` may
record `generated`, but origin does not change identity. An ambient declaration
without exact artifact scope is not promoted to the runtime artifact merely
because its module string resembles a runtime import.

## 5. Runtime-to-declaration mappings

The `runtime-declaration-bindings` fact family is owned by
`csmi.javascript-typescript` `0.1.0`. Each `extensionFact` has:

- family `runtime-declaration-bindings`;
- scope containing one `runtimeSymbol` handle;
- payload kind `runtime-declaration-binding`, the same `runtimeSymbol`, a
  non-empty set of `declarationSymbols`, and relation
  `describes-runtime-binding`.

The runtime symbol MUST use `csmi.javascript-runtime` `0.1.0`; every declaration
symbol MUST use `csmi.typescript-declaration` `0.1.0`. Every handle resolves in
the enclosing semantic model and the declaration symbol carries its own
artifact scope when it comes from a separate artifact. Mapping is directional
and many-to-many. It asserts that the declarations describe the selected
runtime binding in the applicable context; it does not assert symbol equality,
artifact equality, identical overloads, or complete declaration coverage.

The mapping is applicable only when the enclosing runtime artifact selector and
every distinct declaration-symbol selector are `matched`, and every required
runtime and TypeScript compatibility constraint is `compatible`. If any
selector is `not_matched`, that mapping does not apply. If no selector or
constraint is contradicted but one remains indeterminate, the mapping is
indeterminate and MUST NOT be applied by default. Unsupported required identity
or compatibility semantics makes the mapping uninterpretable. A favorable
runtime match never supplies missing declaration-artifact evidence.

Fact equality is exact equality of the runtime symbol plus the set of
declaration symbols and relation. Two facts with the same runtime symbol but
different declaration sets combine by set union only when all artifact and
compatibility contexts are comparable. A declaration mapped to contradictory
runtime symbols in the same exact context is a conflict and makes the mapping
scope uninterpretable.

Completeness scope is exactly one runtime symbol. `complete` means every
declaration symbol known to this profile that describes that runtime binding in
the selected artifact and compatibility context is present. It says nothing
about declarations for sibling exports, runtime behavior, core procedure
summaries, or the completeness of either artifact. Missing declarations,
unsupported resolution, unresolved conditional exports, or an unexamined
overload prohibit `complete` and require `partial` or `unknown` with the
appropriate limitation.

## 6. Node compatibility vocabulary

`csmi.node-compatibility` `0.1.0` defines three compatibility value kinds. Each
constraint is evaluated after core artifact applicability and yields
`compatible`, `incompatible`, or `indeterminate`.

### 6.1 `node-runtime`

This value constrains the execution runtime with one closed structured SemVer
interval. A bound contains a canonical Semantic Versioning 2.0.0 `version` and
an `inclusive` boolean; build metadata is ignored for precedence exactly as
SemVer specifies. A lower bound greater than its upper bound, or equal bounds
where either is exclusive, is semantically invalid. This profile uses a
structured interval rather than VERS because the current VERS registry defines
only npm and PyPI types, neither of which identifies a Node runtime.

Platform and architecture may also be constrained using exact lower-case Node
platform and architecture keys. Missing runtime, platform, or architecture
evidence is indeterminate; contradictory evidence is incompatible.

This compatibility constraint is for npm artifacts whose semantics depend on a
Node runtime. A semantic model whose artifact selector already identifies one
exact Node distribution does not repeat the same version as compatibility.

### 6.2 `node-module-resolution`

This value constrains runtime binding to one module system (`commonjs` or
`esm`), one canonical package export key, and a set of active package
conditions relevant to that export map. The set may be empty when only the
universal `default` branch is used. The producer and consumer derive the
relevant condition keys from the exact selected package artifact, then compare
the active subset as an exact set after sorting by Unicode code point; an
unreferenced active runtime condition is irrelevant. `default` is the universal
fallback and is omitted from this set. `import` and `require` are mutually
exclusive for one resolution. Candidate evidence that selects another target
digest is incompatible. Missing package metadata, selected target, or evidence
for a relevant condition is indeterminate.

### 6.3 `typescript-resolution`

This value constrains declaration binding by a TypeScript compiler SemVer
interval with the same bounds and comparison procedure as section 6.1, a
module-resolution mode, a module kind, active custom conditions, and, when
relevant, JSX mode. If any other compiler option can change the selected
declaration or canonical signature, the value MUST carry
`effectiveOptionsDigest`: SHA-256 over the RFC 8785 canonical JSON object of all
effective compiler options after `extends`, defaults, and command-line
overrides are resolved. Paths are absolute file URIs normalized under RFC 3986;
set-valued option arrays are Unicode-code-point sorted and deduplicated; ordered
option arrays retain order; omitted and explicit default values are distinct.
The candidate consumer constructs the same complete effective-options object.
A consumer lacking comparable configuration evidence reports indeterminate. It
MUST NOT guess from filename extensions, a nearby `tsconfig.json`, editor state,
or source syntax.

Compatibility constraints compose by conjunction. One incompatible constraint
prevents application. If none is incompatible and one is indeterminate, the
model is not applied by default. An unsupported required compatibility use
makes the affected model uninterpretable, which remains distinct from both
outcomes.

## 7. Required fail-closed behavior

A conforming consumer MUST keep these outcomes distinct:

- unsupported `csmi.javascript-typescript` identity: affected symbols and all
  dependent facts are uninterpretable;
- unsupported `csmi.node-compatibility`: affected compatibility is
  uninterpretable, not incompatible;
- understood compatibility with missing project or resolver evidence:
  `indeterminate` compatibility;
- contradicted artifact selector: `not_matched` applicability;
- unresolved artifact selector: `indeterminate` applicability;
- an unresolvable import spelling or computed property: no portable identity,
  with any covering completeness limited; and
- absent facts under `unknown` or `partial`: no negative inference.

Consumers MUST NOT recover by comparing display names, raw module strings,
source text, filenames, CommonJS property spellings, TypeScript signature
display strings, or analyzer-local IDs.

## 8. Canonicalization and dependencies

The profile schemas use JSON Schema Draft 2020-12. Profile payload objects are
closed. String-valued sets (`declarationSymbols`, conditions, platforms, and
architectures) are sorted by Unicode code point and deduplicated before core
canonicalization. `acceptedSpecifiers` is sorted by the tuple (`form`, `value`)
using Unicode code-point order and deduplicated. No profile in this family
depends on another profile version; a model using both declares both uses
explicitly.

The normative conformance cases are in
`conformance/javascript-typescript-node.md`. The representative positive
document is `fixtures/valid/javascript-typescript-node.json`; focused payload
acceptance and rejection fixtures live beside each profile schema.
