# Rust interoperability profile conformance cases

These cases are normative for `csmi.rust` `0.1.0` and
`csmi.rust.source-item` `0.1.0`. JSON fixtures exercise serialization and
payload shape; this file defines semantic outcomes that JSON Schema cannot
establish.

## Positive cases

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Two producers resolve `pkg:cargo/acme-codec@1.4.0`, library target `acme-codec`, and `crate::format::Display` | Same portable key rooted at `lib:acme_codec` | Package, target crate, module ownership, kind, and normalized identifier agree. |
| One producer reads `format.rs`; another reads `format/mod.rs` | Same module key | Filesystem layout is not module identity. |
| `pub use crate::format::Display as PublicDisplay` | One `Display` declaration plus a `reexports` binding named `PublicDisplay` | A reexport binding does not clone its target declaration. |
| `impl Record { fn parse(...) }` split between two source files | Same `Record::parse` key | Inherent items are owned by the nominal type; the impl block and file are not identity. |
| `impl Display for Record` and its `display` body | Implementation key from resolved trait and self type; provided item maps to the exact trait item | Trait ownership and correspondence are structural. |
| `fn decode<T>` used as `decode::<String>` | One declaration key | A use-site instantiation is not a declaration. |
| Package `api-tools` provides library crate `api_core` and binary `api` | Distinct roots `lib:api_core` and `bin:api` under one package selector | Package, target, and crate names are separate identities. |
| Workspace members `api` and `runtime` are both selected | Two package-scoped models plus one exact workspace mapping | Workspace membership does not collapse member artifact identity. |
| `std::mem::drop` resolves to an item declared in `core` | The `core` source-item key plus a `std` reexport binding | Familiar access path does not override defining-crate identity. |
| Named item emitted by a pinned proc macro has exact input/output and generator digests and a normal resolver path | Portable generated source-item key | Reproducible generation and ordinary name resolution are established. |

## Identity near misses

| Left | Right | Expected outcome |
| --- | --- | --- |
| Cargo package name `acme-codec` | crate name `acme_codec` | Different concepts; equality of a normalized spelling is not package-to-crate proof. |
| `lib:tool` | `bin:tool` in the same package | Different source-item roots. |
| Dependency binding `codec` | target crate `acme_codec` | Binding relation required; names are not comparable identities. |
| Module `a::Record` | module `b::Record` | Different descriptor ownership paths. |
| Inherent `Record::display` | provided `display` in `impl Display for Record` | Different owners and implementation paths. |
| Trait declaration `Display::display` | implementation definition for `Record` | Different declarations connected by an `implements` relationship. |
| Generic declaration `decode<T>` | monomorphized binary instance for `String` | Source declaration versus artifact-local codegen entity. |
| `core::option::Option` | a same-spelled item in `std` or another package | Different artifact/crate scopes. |
| Same package/version with features `{std}` | configuration with `{alloc}` | Artifact may match; Rust compatibility is incompatible. |
| Same triple name with different custom-target specification digest | Two custom targets | Incompatible; the name is insufficient. |

## Unsupported and indeterminate cases

| Case | Required outcome |
| --- | --- |
| Consumer supports CSMI core but not `csmi.rust` `0.1.0` required for symbol identity | Affected model and dependent facts are uninterpretable. |
| Consumer supports `csmi.rust` `0.2.0` only | Version `0.1.0` remains unsupported absent an implemented normative mapping. |
| Package selector matches but candidate enabled-feature evidence is missing | Artifact applicability remains matched; Rust compatibility is indeterminate and the model is not applied by default. |
| Registry coordinate matches but required generated-output bytes are unavailable | Applicability is indeterminate when the selector requires their digest. |
| `cfg(target_os = "linux")` item is modeled but candidate `cfg` atoms are unknown | Compatibility is indeterminate, not compatible or inapplicable. |
| Trait and method names match but resolution evidence is absent | Identity/relationship unavailable or partial; no implementation fact is emitted. |
| Macro expansion has compiler-local expansion IDs but no reproducible output evidence | Artifact-local with exact digest, or unavailable; never portable. |
| rustdoc JSON ID, rustc `DefId`, or mangled symbol is equal in two observations | No source-identity conclusion without an exact supported native mapping. |
| Trait implementation self type uses a construct absent from the 0.1.0 type-pattern vocabulary | Implementation identity unavailable and relevant coverage partial/unknown. |
| Candidate has the same sysroot release label but no component digest | Sysroot artifact applicability is indeterminate. |

## Invalid cases

Each case is semantically invalid rather than unsupported or indeterminate:

- a Rust source key without exactly one crate-root descriptor;
- a crate root derived by replacing package-name dashes without a resolved
  Cargo target;
- a module identity derived from a filesystem path;
- an identifier retaining `r#` or not normalized to NFC;
- an implementation disambiguator based on pretty-printed source text, a
  method name, source order, span, `DefId`, or mangled symbol;
- an implementation digest whose canonical `implementation-key` preimage is
  unavailable or does not hash to the descriptor;
- a reexport emitted from import text without a resolver-proven target;
- an unexpanded glob reexport accompanied by `complete` reexport coverage;
- a use-site generic instantiation emitted as a portable declaration;
- a `complete` claim across configurations, compilation roles, packages, or
  profile versions;
- `complete` identity or generation coverage after an unsupported expansion or
  unrepresentable implementation was skipped;
- a `csmi.rust` payload that contains an undeclared property or references a
  missing local symbol; or
- an optional profile use whose removal changes identity, applicability,
  compatibility, binding, relationship meaning, or completeness.

## Requiredness cases

| Use | Valid requirement |
| --- | --- |
| `configuration` compatibility value selecting modeled behavior | `required` |
| `crate-mappings` used to interpret the crate root | `required` |
| `reexports` needed to bind a callable named by a summary | `required` |
| `implementations` needed to apply a trait-method summary to a selected impl | `required` |
| `generation` evidence needed to treat an emitted item as portable | `required` |
| `native-mappings` used only as removable navigation metadata | May be `optional` if removal changes no other result |

## Completeness scopes

Conformance tests MUST distinguish at least these scopes:

1. declaration records for one exact artifact, crate target, Rust
   configuration, identity scheme, and scheme version;
2. reexports for one module and one Rust namespace under that configuration;
3. implementations for one trait or implementing type pattern under that
   configuration;
4. generated items for one generator/output-evidence set; and
5. native mappings for one exact metadata/binary digest and native-system
   version.

Complete-empty is meaningful only after artifact matching, compatible Rust
configuration, exact profile support, valid identity, and all relevant inputs
are established. Unsupported, indeterminate, partial, cancelled, and
budget-exhausted observations do not license negative inference.
