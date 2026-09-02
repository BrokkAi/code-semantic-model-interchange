# JavaScript, TypeScript, and Node profile conformance cases

These cases are normative for the `csmi.javascript-typescript` and
`csmi.node-compatibility` 0.1 profiles. Core structural validity is checked by
`spec/0.1/schema.json`; profile payload structure is checked by the schemas
named in the profile definition.

## Positive binding cases

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Node 22 `require("child_process").execSync` and ESM `import { execSync } from "node:child_process"` | Same `csmi.javascript-runtime` symbol | The exact Node distribution proves both forms resolve to builtin key `node:child_process` and export `execSync`. |
| Node 22 ESM imports `execSync` from bare `child_process` and `node:child_process` | Same runtime symbol | That exact builtin permits the bare alias; the canonical descriptor remains `node:child_process`. |
| TypeScript and TSX projects use the same resolved declaration from one exact `@types/node` artifact under equal TypeScript-resolution constraints | Same declaration symbol | Source-file syntax does not alter the resolver-proven declaration identity. |
| One `@types/node` overload describes Node's runtime `execSync` binding | Valid runtime-declaration binding | The identities remain distinct and are related by an explicit fact. |
| An npm package bundles its `.d.ts` file and runtime export in the same exact package | Shared artifact scope permitted | Both are bytes of the selected npm artifact, while their identity schemes remain distinct. |
| ESM and CommonJS conditions of a dual package both resolve to the same target digest and export binding | Same symbol permitted | Equality follows resolver evidence, not the two syntax forms. |
| An ESM re-export resolves to the same original package export and runtime binding | Same runtime symbol | The re-export path is binding evidence; source module text is not a new identity. |
| A generated `.d.ts` and checked-in `.d.ts` resolve to the same declaration bytes in one exact artifact | Same declaration symbol | `origin` is provenance metadata, not identity. |
| A package export selects only its `default` branch | Empty active condition set | `default` is universal and omitted rather than encoded as an active condition. |

## Near misses

| Case | Expected outcome | Reason |
| --- | --- | --- |
| npm package `child_process` export `execSync` versus Node builtin `node:child_process` export | Different symbols | npm and Node distribution artifact scopes differ; a bare spelling is not package identity. |
| Node builtin requiring a mandatory `node:` prefix versus a same-spelled bare package | Different or unresolved, never aliases | This exact Node registry supplies no bare alias. |
| `import` condition selects `dist/index.mjs`, while `require` selects `dist/index.cjs` with distinct bindings | Different compatible variants | Module form changes the resolved target; use separated compatibility contexts. |
| CommonJS default binding versus a named property with the same display text | Different unless the resolver proves one exported binding | CommonJS/ESM convenience interop does not establish identity. |
| ESM re-export named `execSync` resolves to a wrapper binding rather than the original export | Different symbol | Equal export text does not override the resolver result. |
| Runtime `execSync` versus two TypeScript overload declarations | Runtime symbol differs from both declarations | The relation is explicit and directional; overload signatures are declaration identities. |
| TypeScript value `Result` versus type `Result` in one merged declaration | Different symbols | The declaration scheme preserves TypeScript declaration spaces. |
| Same package name and export name under different active export conditions | Different or indeterminate | Conditions are compatibility evidence, not ignorable presentation data. |
| An ambient module named `child_process` without an exact declaration artifact | No portable declaration identity | Module-string resemblance cannot supply artifact identity. |
| Computed CommonJS export `exports[name]` where `name` is unresolved | No portable symbol identity | The resolver has not established a stable export key. |
| Static and prototype members have the same name and callable shape | Different symbols | Their paths contain distinct mandatory `meta` receiver descriptors. |
| Call and construct signatures otherwise have equal canonical types | Different declarations | `callableKind` participates in the `tsig-0.1` digest. |

## Applicability and compatibility cases

| Artifact result | Profile evidence | Expected outcome |
| --- | --- | --- |
| Exact Node distribution matches | Registry proves alias and export | Applicable; binding may be interpreted. |
| Exact npm package matches | Node version, module mode, conditions, and selected target all agree | Compatible; facts may be applied. |
| Exact npm package matches | Candidate Node version contradicts the structured SemVer interval | `incompatible`; do not apply the model. |
| Exact npm package matches | Candidate lacks active-condition or selected-target evidence | compatibility `indeterminate`; fail closed. |
| Exact npm package matches | TypeScript mode is known but effective project configuration is unavailable for a required digest | compatibility `indeterminate`; fail closed. |
| Candidate package version is unavailable | Compatibility evidence appears favorable | artifact applicability `indeterminate`; compatibility cannot repair it. |
| Candidate PURL is a different `@types/node` version | Runtime Node PURL matches | Declaration symbol selector is `not_matched`; do not borrow declaration facts. |
| Runtime selector matches and declaration selector lacks comparable version evidence | Runtime evidence is favorable | Mapping applicability is `indeterminate`; do not apply the declaration relation. |

## Unsupported and malformed profile cases

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Consumer lacks `csmi.javascript-typescript` `0.1.0` and the use affects identity | Affected symbols and dependent facts are uninterpretable | Opaque descriptor comparison is forbidden. |
| Consumer lacks `csmi.node-compatibility` `0.1.0` | Affected compatibility is uninterpretable | Unsupported semantics are not `indeterminate` evidence. |
| Consumer supports profile `0.2.0`, not exact `0.1.0` | Unsupported unless a normative mapping is implemented | Similar versions are not automatically compatible. |
| Runtime-declaration payload contains only `runtimeName` and `declarationName` | Profile-structurally invalid | Names do not resolve CSMI symbol handles. |
| Node runtime constraint uses free-form `>=20 <23` | Profile-structurally invalid | The profile requires explicit canonical SemVer bounds. |
| Producer declares identity profile optional | Semantically invalid use | Removing it changes symbol binding and all dependent facts. |
| Profile payload validates but consumer does not implement its comparison rules | Unsupported | Schema validity is not semantic support. |
| Known profile payload is present without its exact vocabulary-use declaration | Semantically invalid | Payload presence cannot silently opt a model into profile semantics. |

The `tsig-0.1` value in the representative positive fixture is recomputed from
`fixtures/profile-inputs/typescript-signatures.json` by the repository
validator; changing the canonical record or serialized disambiguator alone
therefore fails conformance validation.

## Completeness cases

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Complete `runtime-declaration-bindings` for one runtime symbol lists all applicable declaration symbols | Negative inference only for additional mappings of that runtime symbol | The family scope is callable-specific. |
| Partial mapping lists one overload and has `coverage-limited` | Other declaration mappings may exist | Omission has no negative meaning. |
| Partial core procedure summary for `execSync` | Says nothing about declaration mappings, invocation, I/O, or process effects | The fixture's single transfer is illustrative and does not claim closed behavior. |
| Complete declaration mappings for npm package root export | Says nothing about a `./subpath` export | Export scopes are distinct. |
| Resolver cannot examine a conditional export branch | `partial` or `unknown`; never `complete` | Unresolved required binding prevents complete coverage. |

## Reference analyzer mapping

The detailed non-normative mapping to Bifrost's public semantic-pack and
JavaScript/TypeScript dependency-adapter surfaces is in
[`reference/bifrost-javascript-typescript-node.md`](../reference/bifrost-javascript-typescript-node.md).

An analyzer may compile the positive fixture into its native model as follows:

1. resolve the Node distribution selector and exact compatibility evidence;
2. intern the `csmi.javascript-runtime` descriptor path as its native callable
   identity without replacing it with a display name;
3. bind both accepted builtin specifier forms to that one callable only after
   its Node resolver proves the alias;
4. compile the core parameter-to-result transfer into the analyzer's native
   summary edge; and
5. retain the separate `@types/node` declaration key and explicit mapping for
   type-aware lookup.

The native key, loader, cache, and summary representation remain analyzer-owned.
A native adapter that instead matches the string `execSync`, scans source text,
or treats every module string `child_process` as the builtin is non-conforming.

## Independent consumer demonstration

The analyzer-neutral
[`node-builtin-alias`](https://github.com/BrokkAi/csmi-demo/tree/main/scenarios/node-builtin-alias)
scenario is consumed by a dependency-free Python implementation with no
Bifrost dependency. Its paired pack-off/pack-on evidence resolves the bare
CommonJS and prefixed ESM cases to the same complete structural symbol identity
only under an exact Node distribution selector, while the same-named npm
package remains a near miss. CI also downloads and verifies the selected
official Node archive bytes.
