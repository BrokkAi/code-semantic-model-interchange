# Portable runtime semantic contracts 0.2

Status: **normative standard profile within experimental CSMI**.

This profile exchanges reviewed contracts for runtime values and the evidence
under which an analyzer used them. It preserves three separate identities:
the versioned semantic contract, the analyzed execution target, and each
program occurrence and store. It does not add a compiler IR, query language,
deployment detector, or universal heap model to CSMI core.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, and **MAY** are
interpreted as BCP 14 when capitalized.

## 1. Version and affected units

The vocabulary is `csmi.runtime-values` **0.2.0** and its schema is
`https://csmi.brokk.ai/schema/profiles/runtime-values/0.2/schema.json`.
The containing document remains semantic model **0.1**, serialization
**0.1-json**. Core artifact, provenance, extension, and completeness rules
continue to apply.

The five families are `runtime-contracts`, `runtime-targets`,
`runtime-activations`, `runtime-bindings`, and `runtime-observations`.
Contracts are authored semantic knowledge. Targets and activation records are
evidence about an analysis configuration. Bindings and observations are
analyzer-produced evidence about source and executable operations. A shipped
contract MUST NOT contain invented program occurrences, loads, concrete
environment values, or a fixture's source identities as production evidence.

Every use is required for its exact family and scope. Referenced contracts,
targets, activations, bindings, and their provenance MUST resolve. Context or
key-comparison schemes also have exact versions: support for the enclosing
vocabulary does not confer support for an unknown scheme. Unsupported required
semantics make affected units uninterpretable. Unaffected core facts remain
independently interpretable.

Version 0.1.0 and its schema, fixtures, and exact-artifact meaning are unchanged.
Consumers MAY support both versions as distinct wire forms. A 0.1-only consumer
MUST refuse affected 0.2 facts, even when their JSON looks familiar. Producers
MUST NOT relabel 0.2 facts as 0.1 or manufacture an artifact digest to downgrade
a portable contract. A separately proved exact-artifact specialization may be
exported only when every older obligation is independently satisfied; it is
not a generally lossless conversion.

## 2. Reviewed contract identity and applicability

A contract identifies one semantic root/container surface. Its inventory handle
is local to the document. Portable identity comprises the contract's absolute
identifier, exact version, and semantic content digest. The root/container
labels describe roles in a versioned runtime contract; they are neither source
name matches nor fabricated declarations for arbitrary keys.

The contract definition explicitly chooses one applicability basis:

- **portable**: the reviewed behavior applies across the stated PURL/VERS
  selection and context. It makes no claim to possess or verify distribution
  bytes. Actual artifact digests are not part of this alternative;
- **artifact-specific**: the definition additionally requires actual artifact
  evidence, using core digest algorithm, coverage, and canonicalization rules.
  Missing bytes remain indeterminate; a comparable mismatch rejects that
  specialization.

The enclosing model retains ordinary core artifact selectors. Runtime
selectors are conjunctive with the contract's context requirements and MUST
not broaden the enclosing applicability. PURL and VERS syntax and semantics
are inherited from core section 3.1. A compatible PURL is evidence of package
identity and version scope; it does not establish a source occurrence's
runtime binding or verify a deployed executable.

The semantic digest commits to the versioned definition, including runtime
selectors, context, assumptions, key and lookup rules, result domains,
mutation/effect behavior, and initial origins. Its coverage is **contract
content**, never runtime artifact bytes. Pack, document, source resource,
contract, review, target, activation, and executable observation digests MUST
remain distinguishable in storage, diagnostics, and caches. Neither identical
digest text in different roles nor a signature grants semantic trust.

A producer MUST issue a new contract version and digest for changed meaning.
Two definitions with one identifier/version but different content are a
conflict. Reformatting or reordering a semantic set does not change meaning.
Review approval applies to the exact reviewed content and scope; it does not
automatically cover later versions, wider version ranges, additional realms,
or new completeness claims.

## 3. Target evidence and conditional claims

A target names an exact source partition, its immutable resources, runtime
selection, context, initialization boundary, and evidence provenance. The
runtime may be unknown, an exact version, or a declared compatible range.
Platform, architecture, realm, module mode, and launch mode are independent
dimensions. A missing dimension MUST remain missing or typed unknown; it MUST
NOT be filled from the analyzer host or from the selected contract.

The target evidence distinguishes **declared-target analysis** from a
**deployment observation**. A declared target authorizes reasoning of the form
"under this runtime contract and these assumptions, this source has this
behavior." It does not verify deployment. An observation concerns only the
execution, resources, configuration, and time boundary its producer actually
observed. It neither proves all deployments use that runtime nor proves
absence of later mutation. Artifact-byte verification is a further independent
claim even when deployment version evidence is available.

Structured evidence can include a launch manifest tied to an entry and source
closure, a deployment descriptor tied to a runtime image, or an explicit user
declaration of the analyzed target. Each must carry provenance and immutable
input identities. The consumer must actually implement the metadata's meaning.
An evidence URI, method name, or digest is a commitment to evidence, not proof
that the assertion is true. Schema/conformance validation checks consistency;
the consuming analyzer is responsible for validating and trusting its producer.

Node installed on the analysis host, `@types/node`, a package name, source
extension, import spelling, or a compatible `engines.node` field alone MUST NOT
establish deployment or spread activation through a project. A supported
metadata adapter can use an engines range as a constraint after it establishes
that the metadata belongs to this execution target. Unknown target evidence
cannot be repaired by choosing a convenient contract from the catalog.

In a mixed project, server, browser, test, and build-tool source partitions
remain separate. Shared source may participate in multiple target analyses;
those results retain their target identities. Membership of a source resource
in one Node partition does not remove an unresolved browser interpretation.
Complete coverage of one partition never closes an unenumerated remainder.

## 4. Deterministic applicability and activation

Applicability, review/trust, activation, binding, and observation completeness
are separate judgments. An activation record commits to the exact target,
candidate inventory, policy and review evidence, and result. Candidates are a
semantic set, not a priority list. A consumer MUST examine every candidate
potentially affecting the requested surface/partition, including conflicting,
unsupported, and insufficiently reviewed candidates.

For each candidate, evaluate canonical runtime identity, version scope, actual
artifact digests when required, all context constraints, and initialization
assumptions. Constraints are conjunctive. A proved contradictory constraint
establishes non-applicability. Without contradiction, missing evidence remains
indeterminate and an unimplemented required comparison remains unsupported.
An unknown comparison cannot establish compatibility or disjointness.

For a target version range, matching means the contract covers **every**
permitted version. Mere intersection is insufficient. A disjoint range is
non-applicable. Partial overlap remains indeterminate unless the analysis is
explicitly split into smaller targets and all uncovered alternatives are
retained. Consumers MUST use the VERS ecosystem comparison procedure; lexical
sorting, guessed SemVer, treating a range as one representative version, or
ignoring prereleases/exclusions is prohibited. A bounded implementation may
return unsupported for a valid scheme/range it cannot evaluate.

Review and trust decisions are scoped to the exact contract digest, target
partition, and analysis purpose under an identified policy snapshot. A producer
claiming "reviewed" cannot authorize its own activation. Accepted review
evidence must come from a reviewer trusted by the consumer's configured policy,
and must actually cover the facts/assumptions being used. Unknown, expired,
withdrawn, or mismatched review evidence cannot satisfy the gate. Explicit
disables take precedence over eligibility; catalog presence is not enablement.
An explicit trust override is observable and cannot change an indeterminate
applicability result into proved applicability.

Activation admits a surface only when its candidate inventory is complete for
that scope, target constraints match, required semantics are supported, review
and trust permit use, and there is no unresolved conflict. A record claiming a
match despite missing evidence is semantically invalid. Inactive and uncertain
results are valid facts and MUST survive round trip; they are not empty models.
Incomplete candidate coverage remains indeterminate even when no candidates
are known or every known candidate is disabled: neither closes the unknown
remainder.

### 4.1 Overlap, specialization, and precedence

Two candidates that are proved disjoint do not conflict. Compatible candidates
whose normalized behavior and obligations are identical may coexist; all their
identities and evidence remain in the activation snapshot. Differing behavior,
lookup, origin, key-equality, exception, mutation, or coverage claims for the
same potentially applicable surface conflict. An incomplete or unsupported
candidate inventory cannot establish absence of a conflict.

**There is no implicit precedence in 0.2.0.** An artifact-specific model does
not win merely because it has a digest; neither a narrower version range,
newer contract version, preferred producer, directory order, nor last-imported
record silently overrides another. This version intentionally does not define
an override or supersedes mechanism. Producers with different claims MUST
partition applicability so it is demonstrably disjoint, or consumers MUST
report the overlap as conflicting. Equivalent artifact-specific and portable
claims may be co-selected after each independently meets its requirements.
Missing bytes for a potentially conflicting artifact specialization remain
unresolved; disabling it is an explicit policy decision recorded in the
snapshot, not a guessed fallback.

## 5. Program binding and executable observations

Runtime exposure and behavior describe the platform API. They cannot establish
that an occurrence spelled `process` denotes the runtime root. Binding requires
resolver/binder evidence for the exact occurrence and target. Lexical
parameters, locals, imports, catch variables, declarations, hoisted bindings,
and value-space TypeScript declarations can conclusively exclude a global
binding. Type-only declarations do not strengthen runtime identity. Imports
and aliases require exact module/export and value identity, not text matching.

Global/root/container replacement, aliasing, destructuring, update/loop writes,
reflection, descriptors, proxies, `eval`, `with`, native effects, and unresolved
calls must be accounted for where relevant. A conclusive shadowing exclusion
may be complete. An unknown root is not a conclusive exclusion. Boundaries for
pristine input require initialization and effect evidence from runtime
creation through the observation, including preloads and reachable dependency
effects. A declaration of target intent does not prove absence of those effects.

An observation identifies the full source expression, root binding, exact
container/base value, typed key, executable load, result value, observation
point, and phase. Source ranges must be nonempty and tied to immutable resources
in the target partition. Producer-local integers and raw byte spans alone are
not portable executable identity. For `process.env.CONFIG_TOKEN`, the terminal
load result is distinct from either of the intermediate root/container loads.

Decoded static string properties and exact integer indices are key identities.
This profile does not define RQL syntax or constant folding. Dynamic keys,
symbols, unsupported numeric-string coercions, optional-chain forms, and
unimplemented expressions remain typed incomplete/unsupported. They must not
be omitted from a claimed complete inventory. A consumer can select arbitrary
already-proved static keys without extending CSMI.

An own-value contract cannot label an inherited property, accessor result, or
proxy trap as an environment value. Absence of an own key does not establish
absence of inherited/accessor behavior. That boundary requires lookup evidence;
known incompatible lookup is excluded from this behavior and unknown lookup is
incomplete. There is no spelling-based exception list for problematic keys.

An exact normal read is observed after normal effects. It does not close the
exceptional continuation. Materialization, exceptions, lookup, initialization,
and mutation are independently required evidence. Host-defined behavior cannot
be rewritten as eager or nonthrowing for convenience. Complete observations
require a dependency-closed effect proof at the exact point, including relevant
transitive calls, preloads, native/unknown code, and interleavings. Cancellation,
budget exhaustion, stale evidence, unresolved aliases, or an open dependency
frontier remain typed limitations.

## 6. Stores, keys, writes, and origins

A cell is scoped by runtime invocation, realm, container/storage identity, and
the key under the applicable equality rule. These are semantic identities with
analyzer provenance, not the root name or contract digest. Two analyses of the
same source under different invocations/targets do not thereby share stores.
Shared storage may cross realms only with explicit backing-store and sharing
evidence. Copying a store transfers values at the copy boundary; it does not
retain later cell identity. Unknown sharing MUST NOT be treated as isolation.

Different keys are disjoint only when the applicable equality relation proves
inequality. Different opaque store identifiers likewise do not prove separate
allocation or non-aliasing. A consumer MUST preserve indeterminate equality;
unknown equality cannot justify killing a transfer or certifying a negative.
A platform-defined comparator requires its exact supported semantic scheme;
Unicode lowercasing or an ASCII shortcut is not an implementation of a native
platform's full environment-key equivalence relation.

`key` retains the decoded source key. `storageKey` is present only when
`proof.keyNormalization` is `exact`: the analyzer has proved how that key maps
through runtime string encoding, native name rules, and the selected comparator.
These fields can differ. A decoded JavaScript string does not itself prove
distinct native keys: embedded NUL, invalid surrogate handling, or host encoding
may reject or collapse names. Such cases need a reviewed conversion mapping or
unknown normalization, not special-name exclusions. `exact-string` compares
normalized property keys by exact Unicode scalar sequence and `exact-index`
compares exact integer indices; neither supplies the missing conversion proof.

Access identity, existence, and value origin are independent. An initial own
environment entry may be an external input if present; a missing entry does not
produce an external value. A proved selected-key write changes origin and must
flow through the write's conversion and store semantics. A constant overwrite
does not retain the previous external origin. A normal successful delete removes
that entry; subsequent lookup still needs prototype/accessor and host semantics.
Unknown writes, deletes, aliases, coercion, branch joins, or calls keep affected
origin/effect coverage incomplete. A known write to a provably different key
does not kill the selected key's independent initial source.

The behavior contract describes normal and exceptional write/delete effects
and conversion obligations. It does not claim a complete executable mutation
trace. Such traces and transfers remain the analyzer's responsibility; existing
CSMI procedure summaries and structured locations should be reused when those
weaker portable facts suffice. This profile does not introduce a general
mutation IR or assert native persistence from generic store examples.

`presentValue: "string"` describes initial runtime entries only. It cannot
retype a later application-written value. In particular, ordinary `argv` array
writes preserve the assigned value rather than applying environment-style
string conversion. `requires-contract` records a conversion obligation which
needs additional supported evidence before a write transfer can be exact;
`unknown` leaves its semantics unmodeled. A read after either kind of unresolved
write cannot inherit the initial string/source claim.

## 7. Node mapping and limits

Version 0.2.0 explicitly assigns `pkg:generic/nodejs.org/node` to the Node
runtime family and the standard `vers:semver/` comparison scheme to its release
versions. A generic PURL is not thereby universally SemVer. This assignment is
part of required 0.2.0 interpretation and does not revise the exact-distribution
rule in `csmi.javascript-typescript` 0.1.0. Canonical release versions have no
leading `v`; prerelease/build forms follow SemVer when supported. A reference
consumer may implement only stable `major.minor.patch` interval comparison and
must report unsupported for valid forms beyond that subset. A range is a
reviewed compatibility claim, not evidence that every permitted future release
has been tested.

The substantive examples concern the runtime `process` root and the `env` and
`argv` containers. They use arbitrary names such as `CONFIG_TOKEN` and arbitrary
supported application indices, rather than a benchmark key inventory.
Each mapping declares its exact runtime/context scheme, PURL/VERS coverage,
language applicability, and initialization boundary. JavaScript, TypeScript,
and TSX share a runtime contract only after their binders and executable-source
mapping independently prove the occurrence.

For a qualifying own environment-value lookup, present values are strings and
absence can produce `undefined`. Assignments may perform string conversion and
deletion removes a selected entry. Conversion and its effects need a reviewed
contract for the applicable runtime version; arbitrary object conversion may
invoke user code. These facts do not imply immutable containers, a nonthrowing
complete read, or ordinary prototype-free property semantics. See the pinned
[Node 22.11.0 process API](https://nodejs.org/download/release/v22.11.0/docs/api/process.html#processenv).

The pinned implementation's environment getter declines interception when no
entry is found, so prototype lookup is a material near miss. Its setter invokes
string conversion, and descriptor operations have separate rejection paths.
This supports retaining separate lookup, conversion, and exceptional evidence;
it does not establish whole-program effect closure. See the
[Node 22.11.0 environment implementation](https://github.com/nodejs/node/blob/v22.11.0/src/node_env_var.cc).

Windows main-thread environment keys are case-insensitive; a worker's copied
environment is case-sensitive. The contract and store evidence therefore retain
both platform and realm. A portable consumer without the relevant equality
implementation returns unknown/unsupported comparison rather than treating
case-distinct keys as separate. Unknown platform or worker mode also prevents
disjointness. See the [versioned environment contract](https://nodejs.org/download/release/v22.11.0/docs/api/process.html#processenv).

Workers normally receive environment copies. The `env` constructor option may
provide different initial values, and `SHARE_ENV` permits shared reads and
writes. Copied environments need a copy boundary and subsequent independent
store state. Shared environments need backing-store identity and concurrency
effects; they cannot inherit a main-thread pristine proof. Unsupported native
equality on shared Windows storage remains explicit. See
[Node 22.11.0 worker environment options](https://nodejs.org/download/release/v22.11.0/docs/api/worker_threads.html#worker_threads_worker_share_env).

For ordinary script launch, initial `argv[0]` denotes the executable path,
`argv[1]` the script entry path, and supported indices from 2 onward application
arguments. Reads beyond actual length may yield `undefined`; no index's
existence follows from its static identity. Environment input, application
arguments, and launcher metadata have distinct origins. See the
[Node 22.11.0 argv contract](https://nodejs.org/download/release/v22.11.0/docs/api/process.html#processargv).

Eval, stdin, REPL, and worker launch must use their own reviewed origin mapping.
They cannot inherit the script's second-slot role or application-argument
offset. When a launch mode has no supported mapping, activation or observation
is unsupported/indeterminate for that claim. No fixture or target default may
silently choose script launch. The
[Node 22.11.0 CLI](https://nodejs.org/download/release/v22.11.0/docs/api/cli.html)
is an input to reviewing those mappings, not proof of a particular program's
launch configuration.

## 8. Independent mapping and semantic conservation

The corresponding CPython family is `pkg:generic/python.org/cpython`, whose
version comparison is `vers:pypi/` under PEP 440. The explicit mapping is owned
by this version of the profile, not by generic PURL semantics. Unsupported
PEP 440 comparisons must not be guessed from SemVer.

Python `os.environ` demonstrates a second ecosystem: resolver-proven module
and export identity expose a mapping rather than a JavaScript global object's
property surface. A present mapping entry is a string; indexed lookup of a
missing key raises rather than returning JavaScript `undefined`. The mapping
captures the process environment when `os` is first imported; later external
environment changes and direct `putenv` calls do not simply make it a live view.
Its import/startup boundary and update behavior must therefore stay distinct
from Node's host container. See the
[Python 3.13 environment documentation](https://docs.python.org/3.13/library/os.html#os.environ)
and [mapping lookup contract](https://docs.python.org/3.13/library/stdtypes.html#mapping-types-dict).

Both mappings retain contract/target/store identity, comparison uncertainty,
normal versus exceptional effects, and scoped completeness. They conservatively
erase implementation-specific heap layouts and retain unsupported lookup or
conversion as uncertainty. Neither maps every runtime property to an initial
external source. The portable contract algebra is shared; runtime-specific
context meanings and resolver evidence are versioned mapping obligations.

## 9. Canonicalization, merging, and cache identity

Core JCS and deterministic-set normalization (section 3.7.5) apply. All arrays
introduced here are sets unless the schema/profile explicitly assigns an
ordered path or ordinal. Key-range records are sets with explicit endpoints,
not array-position semantics. Duplicate identical set members normalize away;
duplicate semantic identities with different payloads are not duplicates and
must be retained as conflicts or rejected as contradictory declarations.

Contract semantic digests exclude local inventory handles and digest fields
themselves. Target digests include evidence basis, source partition and inputs,
not just runtime coordinates. Activation digests include the full candidate and
review/trust decision snapshot, including disabled, rejected, unsupported, and
potentially conflicting candidates. Byte-level resource digests continue to
hash the exact supplied bytes; a consumer cannot repair a bad resource digest
by canonicalizing it after receipt.

The precise SHA-256 inputs are the normalized `definition` object for a
contract or target. An activation hashes an object with `targetDigest`,
`surface`, `contracts` (the complete candidate records resolved from
`candidateIds`), `candidateCoverage`, `disabledIds`, `reviews`, `policy`,
`outcome`, and `selectedIds`. It excludes its own `activationDigest`, local
`activationId`, and local `targetId`. Candidate records retain inventory IDs and
provenance so a changed analysis inventory or review trace invalidates the
snapshot even when equivalent contract content is unchanged. These snapshots
are immutable analysis identities, not cross-document semantic equality keys.

`proof.closureDigest` is the SHA-256 of the normalized `proof` object excluding
`closureDigest` itself, including its evidence commitment. It detects changed
proof assertions or evidence; it is not independently a proof of dependency
closure. Each `evidence.inputsDigest` commits to the immutable evidence inputs
under its producer's exact method, resolved through core provenance. These
inputs may be external: a wire validator cannot recompute their contents from
the digest alone. The consumer must resolve and validate the required evidence
before trusting an exact observation.

`locatorDigest` commits to a normalized object containing `scheme` (absolute
identifier and exact version), `kind`, and a scheme-defined structured
`locator`. `ownerDigest` identifies the immutable source or execution evidence
owning that locator. Every identity also carries that exact `scheme` on the
wire. The structured locator and its derivation must be available through the
record's evidence/provenance, not inferred from names or hashes. Equality
requires the same supported scheme/version, owner, kind, and locator commitment.
Identical hashes with different or unsupported schemes establish neither
equality nor disjointness. Missing scheme fields are invalid; unsupported
identity evidence prevents exact interpretation of the affected observation,
without invalidating independently supported contract activation. The fixture
producer uses an explicitly synthetic locator scheme, not a production binder.

The supported context schemes are
`https://csmi.brokk.ai/runtime-context/node` and
`https://csmi.brokk.ai/runtime-context/cpython`, each at **0.2.0**. Their known
values are defined by this profile's validator and schema: Node realms are
`main`, `worker-copy`, and `worker-shared`; module modes are `commonjs` or
`esm`; launch modes are `script`, `eval`, `stdin`, `repl`, or `worker`; and
initialization boundaries are `runtime-entry` or `application-entry`. CPython
realms are `main` or `subinterpreter`, module mode is `python`, launch modes
are `script`, `module`, `command`, `stdin`, or `repl`, and initialization
boundaries are `module-import` or `application-entry`. Both define `linux`,
`darwin`, `windows` platforms and `x64`, `arm64` architectures. Unknown target
dimensions use `unknown`; new schemes/versions are unsupported until negotiated.
Known schemes with misspelled values are invalid, not aliases.

Key-equality scheme identifiers have the prefix
`https://csmi.brokk.ai/key-equality/`, with `exact-string`, `exact-index`, and
`platform-defined` at **0.2.0**. The last explicitly records a native comparator
obligation and cannot prove key equality/inequality in the bounded reference
consumer. No native Windows Unicode folding algorithm is standardized here.
These scheme versions are part of required 0.2.0 interpretation, not separate
implicitly supported core vocabularies.

A copied store includes `copiedFrom` and `copyPoint`; its backing identity is
distinct from the source. Invocation, realm, and backing identities may share
an execution-evidence owner across target partitions, allowing explicit shared
storage. Container and executable identities remain source-owned. Equal
backing identities across realms require explicit sharing evidence. Different
opaque identities alone establish no disjointness.

Bindings/observations merge only after references resolve and all source,
target, activation, invocation/realm/store, operation, result, point, and phase
identities agree. A contract identifier alone is not a merge key for executable
observations. Contradictory exact observations cannot yield complete coverage.
Completeness remains separately scoped to each fact family and partition.

Caches must include vocabulary/schema/comparator versions, normalized contract
content, target evidence, source and dependency closure, scoped review policy,
candidate inventory, activation decision, store/key equality, and effect proof.
Changing model contents under a stable handle must invalidate dependent results.
Lossless round trip preserves every required fact, condition, uncertainty,
reference, provenance record, and digest role. A consumer unable to do so MUST
refuse lossless export.

## 10. Evidence and scope of conformance

The schema checks payload structure; the dedicated validator checks reference,
scope, digest, applicability, conflict, and proof consistency. Executable
conformance inputs distinguish invalid documents from valid documents recording
conflict, unsupported, unknown, or conditional results. Serialization and a
reference consumer exercise negotiation and deterministic outcomes independently
of Bifrost internals. Their evidence does not certify the reviewed truth of
every runtime version, a production adapter, or deployment.

See the [conformance matrix](../../../conformance/runtime-values-0.2.md) and
[Bifrost follow-up contract](../../../reference/bifrost-runtime-contract-migration.md).
Security-policy acceptance remains independent: URI encoding is not shell
sanitization; no sanitizer kill effect is introduced. Missing semantic support
cannot be repaired by benchmark-specific key exclusions, weakened completeness,
or treating an inconclusive zero-finding result as clean.
