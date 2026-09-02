# CSMI Rust interoperability profile 0.1.0

This document defines the standard vocabulary `csmi.rust` version `0.1.0` for
CSMI 0.1. It is normative. The vocabulary schema identifier is
`https://csmi.brokk.ai/schema/profiles/rust/0.1/schema.json`; the repository copy at
`profiles/rust/0.1/schema.json` is authoritative.

The profile defines one source-item identity scheme, Cargo and sysroot
applicability rules, Rust compilation compatibility, and Rust-owned fact
families. It does not change the language-neutral CSMI core.

## 1. Conformance boundary

A producer or consumer claiming `csmi.rust` `0.1.0` support MUST implement:

- the `csmi.rust.source-item` scheme at scheme version `0.1.0`;
- every payload kind in the profile schema;
- the comparison, requiredness, fail-closed, and completeness rules below; and
- the normative cases in `conformance/rust-profile.md`.

Support is an exact identifier-and-version claim. Schema validation alone is
not semantic support. A use that affects identity, artifact applicability,
configuration compatibility, binding, relationship meaning, or completeness
MUST be declared `required`. Presentation-only provenance annotations MAY be
optional only when removing the complete use changes no supported result.

The following Rust-specific families are defined:

| Family | Scope | Meaning |
| --- | --- | --- |
| `crate-mappings` | one semantic model | Cargo package, target crate, workspace, dependency-binding, or sysroot mapping |
| `reexports` | one exporting module symbol | Resolver-proven binding from an exported Rust name and namespace to a target symbol |
| `implementations` | one trait implementation symbol | Trait implementation ownership and associated-item correspondence; inherent items use ordinary nominal-type ownership |
| `generation` | one generated or generating symbol | Portability classification and reproducible generation evidence |
| `native-mappings` | one source symbol | Explicit, evidence-bearing mapping or non-mapping to metadata or binary identity |

Facts compare only within this exact profile version. Each family uses set
union for non-conflicting facts. Two facts with the same family-defined key and
different payloads conflict; a consumer MUST preserve the conflict and MUST NOT
choose one by input order.

## 2. Cargo artifacts and crates

### 2.1 Package identity

A published Cargo package MUST use its canonical `pkg:cargo` PURL and exact
version or Cargo VERS constraint under CSMI section 3.1. A path, Git, patched,
vendored, locally built, or repackaged package MUST additionally carry a digest
covering the exact package source archive or a canonically serialized source
tree. A registry package whose modeled behavior depends on generated output,
selected features, or other build results not fixed by the published archive
MUST carry exact-content evidence for those results or use a separate semantic
model whose required Rust configuration makes applicability decidable.

A Cargo package is not a crate. One package may define a library, multiple
binaries, examples, tests, benches, a proc-macro library, and a build script.
Each compiled target is a distinct crate. The `crate-mappings` family MUST name
the Cargo target kind, manifest target name, resolver-visible crate name,
compilation role (`host` or `target`), and package PURL. The default conversion
of dashes to underscores is applied only when Cargo resolves the target name
that way; consumers MUST NOT recreate crate identity by applying a heuristic to
the package name.

An `extern crate` name or dependency rename is a binding in the dependent
crate, not the dependency package or target identity. A `dependency-binding`
payload relates that resolver-proven local binding to the exact target crate.
Matching a dependency binding, package, or crate by equal spelling alone is
non-conforming.

### 2.2 Workspaces and resolution

A workspace is a resolution/build context containing packages; it is not a
replacement package identity. Every modeled workspace member MUST retain its
own artifact selector. A `workspace` payload lists exact member PURLs and the
selected member PURLs for the modeled invocation. If membership or selection
changes relevant semantics, the use is required and the package models MUST be
separated or constrained accordingly.

Cargo resolver version and the resolved enabled-feature set are compatibility
inputs, not parts of a source-item descriptor. Resolver version means Cargo's
declared resolver algorithm, not the Cargo executable version. The feature set
is the final resolver output for one package instance and compilation role;
requested command-line features are not an equivalent substitute.

### 2.3 Sysroot crates

`core`, `alloc`, `std`, `proc_macro`, and other sysroot crates are distinct
crate identities. They MUST NOT be modeled as Cargo registry packages or as
aliases of one another. A sysroot model uses an exact-version
`pkg:generic/rust-sysroot@<release>` selector plus a digest for the covered
sysroot distribution or component bytes. Its `sysroot-crate` payload repeats
that exact selector as `artifactPurl` and names the component crate,
compilation target, compiler release, and component digest. The payload link
MUST equal one of the enclosing model's artifact-selector PURLs; matching only
the release string is insufficient.

Reexports between sysroot crates use the same `reexports` family as application
crates. The familiar path `std::...` therefore does not change the identity of
an item declared in `core`; it is a resolver-proven reexport binding.

## 3. Rust compilation compatibility

The `configuration` payload is used as the value of a `csmi.rust` compatibility
constraint. It describes the configuration under which already-selected
artifact semantics hold. It MUST include:

- Rust edition;
- compiler release and, when nightly/unstable or compiler-dependent behavior
  matters, the compiler commit hash;
- Cargo resolver version;
- target triple, or a stable name plus SHA-256 digest for a custom target
  specification;
- the exact enabled feature set for the package instance and compilation role;
- the exact normalized `cfg` atom set observed by the crate after target,
  `--cfg`, feature, and build-script contributions; and
- when non-default compiler options affect semantics, a SHA-256 digest of the
  RFC 8785 canonical JSON ordered argument vector.

Configuration sets are compared as exact sets after Unicode code-point sorting;
`cfg` atoms are pairs of a key and optional value, not source expressions.
Consumers MUST NOT evaluate unrecorded `cfg(...)` source text, infer features
from dependency names, assume host equals target, substitute the package
`rust-version` for the actual compiler, or treat an unknown custom target as a
known triple.

Compatibility is `compatible` only when every required field is understood and
equal. A comparable unequal field is `incompatible`. Missing candidate
evidence is `indeterminate`. An unsupported required profile is
`uninterpretable`. All but `compatible` fail closed and do not change the
separate artifact-applicability result.

Edition is ordinarily a property of the selected crate target. Compiler
release, target, features, resolver, `cfg`, and flags are compatibility inputs
when the modeled fact varies with them. When any such input selects different
artifact bytes and exact content is available, the selector SHOULD also carry
the corresponding digest; compatibility metadata never makes unequal bytes
equal.

## 4. Deterministic source-item identity

### 4.1 Key and normalization

A portable Rust item uses scheme `csmi.rust.source-item`, scheme version
`0.1.0`, stability `portable`, and the enclosing model's exact artifact scope.
Its descriptor path starts with exactly one crate-root descriptor:

```json
{ "role": "namespace", "name": "crate", "disambiguator": "lib:acme_codec" }
```

The disambiguator is `<target-kind>:<resolver-crate-name>`, where target kind is
one of `lib`, `bin`, `example`, `test`, `bench`, `proc-macro`, or
`build-script`. Colons and percent signs in either component are percent-encoded
with uppercase hex. This root is derived from the resolved Cargo target, never
from an import spelling, output filename, mangled symbol, or package-name guess.

Following descriptors represent the resolver ownership path. Modules use role
`namespace`. Types, traits, unions, enums, and type aliases use role `type`.
Functions and associated functions use role `callable`; constants, statics, and
enum variants use role `term`; macros use role `meta`; generic parameters use
`type-parameter` or `value-parameter`. Every named descriptor uses the
resolver-normalized identifier: remove a raw-identifier `r#` prefix and compare
the resulting identifier by Unicode code points after NFC normalization. Case
is significant.

Each non-parameter descriptor has a required kind disambiguator (`module`, `struct`, `enum`,
`union`, `trait`, `type-alias`, `function`, `method`, `associated-function`,
`const`, `static`, `variant`, `macro-rules`, `macro`, `proc-macro-function`,
`proc-macro-derive`, `proc-macro-attribute`, `type-parameter`,
`const-parameter`, or `lifetime-parameter`). This distinguishes Rust namespaces
and declaration kinds; it is not a display signature. A generic-parameter
descriptor instead uses its zero-based decimal declaration position as `name`
and its parameter kind as `disambiguator`; the source identifier is display
metadata only.

Module identity follows resolved module ownership, not file paths. Inline,
`mod.rs`, non-`mod.rs`, and `#[path]` layouts that resolve to the same module
produce the same descriptor path. A `use` item or alias does not mint a second
declaration identity.

### 4.2 Declarations, generics, and uses

Named module items and named inherent associated items are owned by their
resolved module or nominal type. Rust does not permit source overload sets in
one such namespace, so parameter or return spelling is not used to distinguish
them. A declaration's generic type, const, and lifetime parameters are owned by
that declaration and identified by kind plus zero-based declaration position;
renaming a generic parameter does not change its identity. Bounds and where
clauses are declaration facts, not identity.

A generic use, inferred instance, monomorphization, vtable entry, shim, or
codegen unit is not a new portable source declaration. It refers to the generic
declaration plus explicit type/const arguments in the consuming fact. A
consumer MUST NOT mint identities from pretty-printed substitutions or mangled
symbols.

Local variables, labels, anonymous constants, closures, async/generator state
machines, and compiler-synthesized entities have no portable identity in this
version. They MAY use `artifact-local` identity only when every alternative
artifact selector carries an exact digest and a supported native mapping proves
the entity in those exact bytes. Otherwise they are unavailable and relevant
coverage is `partial` or `unknown`, never silently complete.

### 4.3 Traits and implementations

A trait and each trait associated-item declaration have ordinary portable
identities under the trait's ownership path. An inherent associated item is
owned directly by its nominal type; an inherent `impl` block does not create a
portable declaration and source-file placement does not affect identity.

A trait implementation is a portable meta item only when its trait and
implementing type pattern are resolver-proven and encodable by this profile.
Its final descriptor is:

```json
{ "role": "meta", "name": "impl", "disambiguator": "jcs-sha256:<64 lowercase hex>" }
```

The digest covers the RFC 8785 canonical JSON serialization of an
`implementation-key` payload containing the exact trait symbol key, the
implementing type pattern, and positional generic binders. Symbol keys include
artifact scope, scheme, scheme version, stability, and descriptors. They MUST
NOT be replaced by local handles or names. Type patterns use only the variants
defined by the profile schema. If a pattern cannot be represented, the
implementation is unavailable under 0.1.0 rather than approximately named.
Before RFC 8785 serialization, every set-valued array inside the key is ordered
by the CSMI 0.1 canonicalization rules; ordered descriptor and type-argument
arrays retain their semantic order.

An item defined by a trait implementation is owned by the implementation
symbol. An `implementations` fact relates it to the implementing type, trait,
and, for each provided item, the exact trait declaration. A default trait item
used without an overriding definition retains the trait declaration identity;
dispatch evidence identifies the selected implementation separately. A method
name match, compatible-looking signature, UFCS spelling, or autoderef result is
not proof of ownership or correspondence.

Negative implementations use a distinct `negative-trait` kind and have no
associated items. Blanket and generic trait implementations use the same
structured type-pattern rules. Inherent impl blocks have no implementation
symbol or `implementations` fact; only their nominal-type-owned associated
items are portable. The profile does not infer coherence, specialization, or
dispatch from the presence of an implementation fact.

### 4.4 Reexports and aliases

A reexport fact is keyed by exporting module, normalized exported name, and
Rust namespace (`type`, `value`, or `macro`) and targets one resolver-proven
symbol. Glob reexports MUST be expanded to individual bindings for the modeled
configuration. Private imports may be represented as bindings only when a
profile-owned family explicitly requests them; they are not public reexports.

Two bindings with the same spelling but different namespaces remain distinct.
An alias, `self` import, `crate`, `super`, extern prelude entry, or dependency
rename is interpreted only after resolver proof. Source text and path spelling
alone are insufficient. Reexport completeness is scoped to one exporting
module, namespace, exact configuration, and this profile version.

## 5. Generated and macro-related items

A named `macro_rules!` declaration or procedural-macro declaration has the
ordinary portable identity described above. A macro invocation is not itself a
portable declaration merely because it has a source location.

A named expanded item MAY be portable when normal Rust name resolution assigns
it a source-item key and the producer records sufficient `generation` evidence:

- generator kind and exact generator symbol when one exists;
- exact proc-macro/build-script artifact identity and digest where applicable;
- digest of the canonical input token stream or build inputs;
- digest of the generated token stream or source bytes; and
- exact Rust configuration under which generation occurred.

Only an explicit `unavailable` classification MAY omit the input/output
digests. An `artifact-local` classification still requires the output digest
plus exact-content artifact scope in the enclosing model.

Every `portable` or `artifact-local` generation fact MUST be enclosed by one
exact `csmi.rust` `configuration` compatibility constraint. That constraint is
the generation configuration; producers MUST NOT duplicate a partial
configuration inside the payload. A consumer that cannot establish it treats
the generation fact as indeterminate. An `unavailable` fact MAY omit the
constraint only when no portable or artifact-local conclusion depends on it.

If deterministic regeneration or equivalence cannot be established, the item
is `artifact-local` with exact-content scope or unavailable. Hygiene contexts,
compiler expansion IDs, syntax-context integers, spans, traversal order, and
incremental-compilation IDs are not portable identity.

Build-script-generated Rust source follows the same rule. A named item in exact
generated source may receive the normal source-item identity if the generated
bytes and module inclusion are part of applicability evidence. Compiler-
synthesized shims, drop glue, closure bodies, async state machines, and
monomorphized instances are never portable source items in 0.1.0.

## 6. Metadata and binary mappings

`csmi.rust.source-item` identifies source-language declarations. It does not
identify a stable Rust ABI, rustc metadata record, MIR body, LLVM item, DWARF
entry, vtable slot, or linker symbol. Rust v0 and legacy mangled names,
demangled display strings, `DefId`, `DefPathHash`, crate disambiguators, and
rustdoc JSON IDs MUST NOT be treated as equivalent source identity.

The `native-mappings` family makes the boundary explicit. A mapping names the
native system and version, exact metadata or binary digest, compiler release
and target when relevant, cardinality, and status:

- `exact` means the stated source key and native identity are proven to denote
  the same entity in the exact artifact;
- `conditional` means the relation holds only under the recorded configuration
  and remains uninterpretable without it; and
- `none` explicitly declines a mapping and MUST NOT be repaired by names.

Mappings are artifact-local evidence and do not merge across binary, metadata,
compiler, target, or profile versions. One source item may map to many native
items and one native item may implement several source-level obligations; a
consumer MUST preserve declared cardinality. A binary symbol discovered with
no proven source key remains a native entity outside this source scheme.
Every `conditional` mapping MUST be enclosed by exactly one `csmi.rust`
`configuration` compatibility constraint, which supplies the recorded
configuration referred to by the status.

## 7. Completeness and fail-closed behavior

Core completeness remains scoped as specified by CSMI 0.1. Rust profile-family
completeness additionally includes the exact artifact selectors, Rust
configuration, `csmi.rust` version, identity scheme version, family, and family
scope. Separate configurations, crates, compilation roles, and sysroot targets
are not comparable scopes.

A `complete` claim is forbidden when relevant items or facts were skipped
because of unsupported expansion, unrepresented type patterns, unresolved
bindings, missing build-script output, unknown features or `cfg`, absent
compiler/target evidence, unsupported native mapping, cancellation, or budget.
The producer MUST use `partial` with an appropriate limitation or `unknown`.

The following outcomes remain distinct:

| Condition | Required outcome |
| --- | --- |
| Artifact selector contradicted | `not matched` |
| Valid selector lacks digest/package evidence | applicability `indeterminate` |
| Required Rust profile/version unsupported | affected units `uninterpretable` |
| Profile understood but configuration evidence missing | compatibility `indeterminate` |
| Configuration evidence contradicted | `incompatible` |
| Identity cannot be resolver-proven or represented | unavailable/partial identity coverage |
| Supported, applicable complete scope with no facts | complete empty set for only that scope |

No fallback may turn any of the first six rows into the last. In particular,
consumers MUST NOT use names, mangled symbols, source text, filesystem paths,
display signatures, or compiler-local IDs to make an indeterminate or
unsupported case appear resolved.

## 8. Reference analyzer mapping (non-normative)

An analyzer may map its resolver-owned Rust declaration identity to the crate
root and ownership descriptors above, map resolved import edges to `reexports`,
and map trait-selection results to `implementations`. For rust-analyzer, syntax
nodes and displayed paths are only lookup inputs: the mapped identity must come
from resolved crate/module/definition ownership, and unresolved or macro-only
syntax stays incomplete. rustdoc JSON `Id` values may be recorded only through
`native-mappings` with the exact rustdoc format/toolchain and artifact digest.

Bifrost can follow the same boundary by exporting its resolved declaration and
usage graph into CSMI keys while keeping analyzer database IDs, internal FQNs,
compiled semantic-pack keys, and query-engine state private. This mapping is an
implementation example, not a normative dependency on either analyzer.

| Analyzer evidence | CSMI mapping | Required stop condition |
| --- | --- | --- |
| Resolved Cargo package and crate graph | Artifact selector plus `crate-target`, `workspace`, and `dependency-binding` facts | Missing package provenance, target identity, or final resolver output |
| Resolved module/declaration ownership | `csmi.rust.source-item` descriptors | Syntax-only path, display FQN, or unresolved macro expansion |
| Resolved import/reexport edge | `reexports` fact | Name or source import text without a target identity |
| Resolved trait impl and associated-item correspondence | Implementation key plus `implementations` fact and core `implements` relationship | Same-spelled member or signature resemblance without resolver proof |
| Expanded named declaration with reproducibility evidence | Source-item symbol plus `generation` fact | Compiler-local expansion/span ID or missing exact generator/input/output evidence |
| rustdoc/rustc metadata or binary correlation | `native-mappings` fact scoped to exact bytes and toolchain | Opaque ID, mangled symbol, or demangled string without a proven correlation |

An implementation that reaches a stop condition reports partial, unknown,
unsupported, or indeterminate state at the affected scope. It does not emit an
approximate mapping.

## 9. Change control

Adding a type-pattern variant, changing descriptor construction, changing
configuration comparison, or changing family equality/completeness requires a
new profile version. Editorial clarifications that do not change producer or
consumer outcomes do not.

## 10. Normative references

- [Rust Reference: implementations](https://doc.rust-lang.org/reference/items/implementations.html)
  and [associated items](https://doc.rust-lang.org/reference/items/associated-items.html)
  define the language ownership distinctions used by this profile.
- [Rust Reference: conditional compilation](https://doc.rust-lang.org/reference/conditional-compilation.html)
  defines configuration options as names or name/value pairs and their effect
  on item inclusion.
- [Cargo Book: targets](https://doc.rust-lang.org/cargo/reference/cargo-targets.html),
  [workspaces](https://doc.rust-lang.org/cargo/reference/workspaces.html),
  [features](https://doc.rust-lang.org/cargo/reference/features.html), and
  [dependency resolution](https://doc.rust-lang.org/cargo/reference/resolver.html)
  define the package, crate-target, workspace, feature, and resolver concepts
  reused here.
- [Package-URL type definitions](https://github.com/package-url/purl-spec/tree/main/types)
  remain authoritative for canonical PURL type behavior.
- [RFC 8785](https://www.rfc-editor.org/rfc/rfc8785) defines JSON
  canonicalization for implementation-key digests.
- [rustdoc JSON `Id`](https://doc.rust-lang.org/nightly/nightly-rustc/rustdoc_json_types/struct.Id.html)
  documents that its values are opaque and local to one JSON blob, supporting
  the explicit non-portable mapping boundary in section 6.
