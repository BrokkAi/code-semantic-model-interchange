# Runtime exposure and keyed-read values profile 0.1

Status: **normative standard profile**.

This profile defines analyzer-neutral contracts for runtime-global exposure and keyed value reads. It supplements CSMI 0.1 without turning runtime globals or arbitrary map/array keys into declarations. The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**, and **MAY** are interpreted as BCP 14.

## 1. Identity and negotiation

The required vocabulary is `csmi.runtime-values` version `0.1.0`, with schema `https://csmi.brokk.ai/schema/profiles/runtime-values/0.1/schema.json`. A use affects its exact fact family and scope. A consumer that cannot implement this version MUST report affected facts as uninterpretable; it MUST NOT discard them and treat their scope as empty, exact, or complete.

The four families are `runtime-global-exposures`, `keyed-read-behaviors`, `runtime-global-binding-evidence`, and `keyed-read-observations`. Exposure and behavior records are producer-authored runtime contracts. Binding evidence and observations are producer-authored analysis results about particular source operations. The latter MUST NOT acquire portable identity from producer-local dense identifiers; operation, value, and point strings are document-local handles whose meaning is fixed by immutable source-resource digests, source correspondence, provenance, and the enclosing artifact.

## 2. Runtime-global exposure

A `runtime-global-exposure` identifies a binding made available by an exact runtime execution profile. Runtime family, exact versioned artifact PURL, realm, module mode, initialization boundary, language/dialect applicability, activation status, evidence inputs, and coverage participate in applicability. A Node declaration package, a source file extension, a binding name, or catalog availability alone does not activate an exposure.

`rootIdentity` is a profile-defined portable semantic identity. `exposureId` is an inventory identity and is not a core symbol or declaration identifier. `members` names modeled container roles within this profile only; it does not mint declarations for their possible keys.

Exactly one compatible enabled exposure must match before a consumer may establish an exact binding. Disabled and nonmatching exposure is conclusive non-applicability. Missing, conflicting, review-required, incompletely enumerated, or unsupported activation is indeterminate, conflicting, or uninterpretable as appropriate—never an exact global.

## 3. Keyed-read behavior

A `keyed-read-behavior` describes reads from one modeled container role. Static property and index keys are value-access identity, not declaration identity. A property is its decoded string. An index is an exactly represented integer from 0 through 2^32-2. Profiles may further restrict accepted forms. Dynamic keys, arithmetic expressions, symbols, negative/fractional/oversized indices, and unimplemented language coercions do not become static keys.

Normal value, exception, mutation, accessor/proxy, and materialization semantics are independent obligations. `value-or-undefined` asserts neither key existence nor concrete value type. Container shape alone does not prove behavior. Unknown accessors, proxies, descriptors, prototype mutation, lazy materialization, host effects, or exceptions require partial/unknown coverage unless the contract and observation evidence explicitly cover them.

## 4. Per-access evidence

`runtime-global-binding-evidence` relates one source occurrence to an exposure and activation snapshot. The snapshot names its activation source and commits to runtime-profile, active-set, and selected-model digests; catalog presence is not activation. Exact binding requires `matched` activation, absent lexical binding, excluded rebinding, and complete evidence. Parameters, locals, imports, catch bindings, classes, functions, hoisted `var`, and TypeScript value bindings are conclusive shadowing. Type-only constructs and ambient declarations do not establish runtime activation. Global-object replacement, destructuring/update/loop assignment, alias or reflective writes, and unknown effects must be covered before rebinding can be excluded.

`keyed-read-observation` identifies the exact base value, typed key, executable load, result value, observation point and phase, and full expression range. `process.env.DFB_INPUT` therefore denotes two container loads and the terminal property load; its observation maps to the terminal result and the full terminal expression. `process.argv[2]` maps to the indexed load result and full indexed expression. A bare container expression is not an element observation.

An exact normal observation does not by itself exclude exceptional behavior. `after-effects` is the normal result phase. Exceptional continuations remain represented independently. Cancellation, budget exhaustion, stale or ambiguous materialization, missing heap state, or incomplete mutation/effect discovery MUST yield partial, indeterminate, or unsupported evidence and MUST NOT be published or reused as complete.

`sourceOrigin` is distinct from access identity. A known selected-key overwrite may leave the access identity exact while changing origin to `mutated`; unknown relevant writes make origin `indeterminate`. A consumer such as a taint policy may require `pristine-runtime-input`, but it may not infer that origin from an exact key alone.

## 5. Applicability, validity, merging, and completeness

Structural schema validity, profile semantic validity, runtime applicability, and consumer interpretability are independent outcomes. Semantic validity additionally requires source ranges with `endByte > startByte`; complete binding evidence with matched activation, absent lexical binding, and excluded rebinding; complete observations whose binding evidence and behavior resolve in the same applicable model; `after-effects` for exact normal load results; and compatible source form/key kinds.

Fact equality is exact payload equality after document-local references resolve. Producer-authored contracts with the same identity but different semantics conflict. Per-access evidence merges only when artifact, activation, source occurrence, operation, result, point, and phase agree; otherwise the observations remain distinct. Contradictory exact observations make the scope uninterpretable.

Completeness is scoped separately to an exposure inventory, a behavior, a binding occurrence, or a keyed-read operation. Completeness in one family never closes another. A filtered consumer MUST preserve residual incompleteness; absence of an exact observation is not proof that no runtime read exists.

## 6. Node mapping

For an exact Node distribution, a profile may expose global `process` with container roles `env` and `argv`. `env` accepts decoded static string properties, including dot and literal-string bracket forms. `argv` accepts numeric literal indices through 2^32-2. String `"2"`, computed `1+1`, optional chains, and dynamic indices remain unsupported until a versioned ECMAScript conversion/optional-chain contract defines them.

The runtime profile retains platform and realm because environment behavior differs across them. Node documentation alone does not prove immutability, absence of accessors/proxies, nonthrowing behavior, or a closed mutation footprint. A profile claiming pristine runtime input must state the initialization boundary and host assumptions and provide complete evidence for relevant preloads, global/container replacement, selected/dynamic writes, descriptors, proxies, prototypes, calls, native effects, `eval`/`with`, and asynchronous interleavings.

JavaScript, TypeScript, and TSX use the same runtime contract only when each dialect's binder and source mapper independently establish the required evidence. Type annotations and assertions do not strengthen runtime proof.

## 7. Round trip

A conforming lossless serializer MUST preserve every record, typed outcome, limitation, source range, document-local identity, activation/provenance digest, and unknown field only when a negotiated later vocabulary permits it. A consumer unable to retain the required vocabulary MUST refuse lossless export. It MUST NOT rewrite these facts as `runtime-declaration-binding`, declaration members, display names, source chains, or empty exact results.
