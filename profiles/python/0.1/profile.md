# CSMI Python interoperability profile 0.1

This document defines the normative `csmi.python` standard profile version
`0.1.0` for CSMI semantic-model version 0.1. It defines Python import-visible
symbol identity, artifact-to-import mappings, runtime/declaration
correspondence, and Python execution compatibility without adding
Python-specific fields to the CSMI core.

The key words **MUST**, **MUST NOT**, **REQUIRED**, **SHOULD**, **SHOULD NOT**,
and **MAY** are to be interpreted as described by BCP 14 when, and only when,
they appear in all capitals.

## 1. Profile identity and support

The profile identifier is `csmi.python`; its exact version is `0.1.0`. Its
payload schema is
`https://csmi.brokk.ai/schema/profiles/python/0.1/schema.json` and uses JSON
Schema Draft 2020-12. Schema acceptance establishes payload structure only.

A model using this profile MUST declare a `vocabularyUses` entry for
`csmi.python` version `0.1.0`. The use MUST identify each affected core slot,
fact-family scope, or attachment. It MUST be `required` whenever it controls
artifact applicability, compatibility, symbol binding, declaration meaning,
completeness, or negative inference. A purely descriptive attachment may be
optional only when removing the complete use leaves every other result
unchanged.

A consumer supports this profile only if it implements the relevant identity,
fact, compatibility, conflict, and completeness rules in this document. Merely
validating the schema, preserving payload bytes, or recognizing the identifier
is not support.

## 2. Artifact and import identity

### 2.1 Distributions are not import packages

An installable Python distribution is selected with a canonical `pkg:pypi`
PURL and exactly one version form under the CSMI core. PEP 503 normalization
applies only to the distribution name through PURL's PyPI rules. It MUST NOT be
applied to import names.

An import package or module is a Python binding, not a package-manager
coordinate. Producers MUST NOT infer an import root from a distribution name,
or a distribution from an import name, by replacing punctuation, case-folding,
inspecting an archive path, or reading display metadata. A distribution's
provided import roots are established only by resolver or installation
metadata evidence and encoded in a `distribution-imports` fact.

One distribution may provide multiple import roots, one import namespace may
have multiple distribution contributors, and a distribution may provide no
importable Python module. These are distinct, valid cases.

### 2.2 Interpreter and standard-library artifacts

Interpreter-distribution and standard-library models use a canonical
`pkg:generic/python-runtime` selector. They MUST include these PURL qualifiers
using PURL's canonical qualifier ordering and encoding:

- `implementation`, containing the lowercase implementation identifier such as
  `cpython` or `pypy`; and
- `component`, containing `interpreter` or `stdlib`.

The PURL version is the exact interpreter language version whose runtime or
standard-library surface is modeled. A producer MUST include an exact-content
digest when the qualifiers and version do not uniquely identify relevant
bytes, including patched runtimes, platform-specific builds, separately
shipped standard libraries, or implementation-bundled native modules.

Because `generic` coordinates are not governed by a package registry, this
profile owns the coordinate convention: the namespace is absent, the name is
exactly `python-runtime`, and no other qualifier changes the artifact's
meaning. A consumer that does not implement this convention reports the
selector as unsupported rather than treating arbitrary `pkg:generic` names as
Python runtimes.

The names `builtins`, `sys`, and other standard-library modules remain module
descriptors under the selected standard-library artifact. A module's apparent
availability in source text or on another interpreter is not applicability
evidence. Bundled third-party distributions retain their own artifact identity
unless the runtime distribution makes them an inseparable, digest-scoped
component.

### 2.3 Runtime and declaration artifacts

Runtime distributions, inline `.pyi` files, separate `*-stubs` distributions,
and typeshed resources are separate evidence sources. A stub distribution uses
its own canonical `pkg:pypi` selector. A typeshed snapshot uses a
`pkg:github/python/typeshed` selector with an exact commit revision as its PURL
version and SHOULD include an archive or repository-snapshot digest.
Neither artifact is substituted for the runtime artifact it describes.

A `declaration-correspondence` fact relates a declaration supplied by a stub or
typeshed artifact to a runtime import-visible symbol. It asserts correspondence
only for the named symbols, direction, and conditions. Matching descriptor
text, filenames, PURL names, or producer-local IDs do not establish the
relationship. Stub completeness closes only the declared profile family and
scope; it does not prove that runtime members exist, are exhaustive, or behave
as declared.

## 3. Import-visible symbol identity

`csmi.python` version `0.1.0` is also the identity scheme and scheme version
defined by this profile. Identity comparison is exact Unicode code-point
comparison of every descriptor role, name, and disambiguator after Python's
resolver has established the binding. Producers MUST NOT apply Unicode
normalization, case folding, PEP 503 normalization, or filesystem case rules.

### 3.1 Descriptor construction

A portable descriptor path begins with one `namespace` descriptor for every
component of the canonical absolute import module. The path then follows
resolver-established declaration ownership:

- a module or package uses the module-component `namespace` path;
- a class, protocol, enum, or type alias appends a `type` descriptor;
- a module or class value, constant, property, or data descriptor appends a
  `term` descriptor;
- a function, method, constructor, property accessor, or other invocation
  target appends a `callable` descriptor;
- a declaration nested in a function or class includes every declaring owner;
  and
- parameters use owner-relative `value-parameter` descriptors only when they
  are semantic targets.

The resolver-established defining name is used for a named declaration
descriptor. An import statement's spelling is not identity. Relative and
absolute imports, aliases, star imports, and re-exports identify the resolved
binding represented by `import-bindings`; an exported alias does not replace
the target's defining descriptor path, and equal text does not mint equal
identities.

`__init__.py`, `.py`, `.pyi`, extension-module filenames, zip members, search
paths, editable-install paths, and namespace-package directories MUST NOT
appear in portable identity. Namespace-package portions use the same module
descriptor path within each contributing artifact, but their core symbol keys
remain distinct because artifact scope is part of identity. Contributors are
recorded by `distribution-imports`; an environment-specific binding view may
combine them only after resolving the complete contributor set, and MUST NOT
silently equate their artifact-scoped symbols.

### 3.2 Callables, overloads, and descriptors

Python runtime dispatch does not select overload declarations by signature.
An import-visible runtime callable therefore has no callable disambiguator when
its owner has only one binding with that name. A producer MUST NOT use a source
ordinal, line, signature hash, annotation spelling, or inferred parameter type
as a runtime callable disambiguator.

Typing overload variants are declaration-only callables. Each appends a
`callable` descriptor with the runtime binding name and a disambiguator of
`typing-overload:<canonical-signature>`. The canonical signature is an object
with `parameters` and `result`; each parameter object has `kind`, `required`,
and `type`, and additionally `name` for keyword-only parameters. A Python type
identity object contains `artifact` with one canonical exact-versioned PURL,
`scheme`, `schemeVersion`, and `descriptors` constructed under that scheme.
Another required profile may define its own canonical type-identity object.
Unions list their canonical member identities in bytewise RFC 8785 order. The
signature excludes parameter names except
keyword-only parameters, whose names participate in call binding. JSON is
canonicalized under RFC 8785 before being embedded after the prefix. A final
implementation declaration, when present, retains the undisambiguated runtime
callable identity. Overload variants MUST NOT be targets of runtime procedure
summaries.

A property is a `term` owned by its class. Its getter, setter, and deleter are
distinct `callable` children named `get`, `set`, and `delete`. Other descriptors
with independently invocable accessors follow the same rule through a required
profile extension; absent such a rule, only the descriptor value is portable.
Decorators do not change identity unless resolver evidence proves that they
replace the exported binding, in which case the binding target is encoded by
`import-bindings` and the replaced declaration is not silently equated.

### 3.3 Aliases, re-exports, and namespace packages

The `import-bindings` family records a binding from an exact owner module and
exported name to one exact target symbol. Its `bindingKind` is `definition`,
`alias`, or `re-export`. Equality is the tuple of scope, name, binding kind,
target symbol identity, and conditions.

Two bindings with different names may target the same symbol. The alias names
are not additional symbol identities. A module that intentionally presents a
wrapper or independently declared object has its own target identity even when
documentation calls it a re-export. Star-import and `__all__` evidence may
establish individual bindings, but the text of either construct is not itself
resolution proof.

Namespace-package contributors are an unordered set in
`distribution-imports`. A consumer MUST establish the applicable resolved
environment before combining contributors. Missing contributor, search-order,
or project-configuration evidence makes binding or applicability
`indeterminate`; it does not license selection of a convenient contributor.

### 3.4 Generated, dynamic, and local declarations

A generated declaration may be portable when normal import and ownership
resolution yields the same binding across conforming producers. The symbol's
core `origin` may be `generated`; generation does not weaken identity rules.

A declaration created only by execution, module `__getattr__`, metaclass
behavior, monkey patching, native extension initialization, or another dynamic
mechanism is portable only when resolver/runtime metadata proves one stable
import-visible binding for the applicable environment. Otherwise it is
artifact-local if the core exact-content requirements and a deterministic
owner-relative construction can be satisfied. If neither is possible, the
producer MUST omit it and report `partial` coverage with an
`unsupported-semantics` limitation, or leave coverage `unknown`.

Display names, import text, filesystem paths, source text, runtime addresses,
reflection traversal order, and producer-local IDs MUST NOT repair unavailable
identity.

## 4. Profile fact families

Collection arrays defined by this profile are mathematical sets and are
serialized in RFC 8785 bytewise order of their canonical JSON elements.
Module-component arrays and canonical-signature parameter arrays are ordered
paths or sequences instead. Duplicate set elements are semantically invalid.

### 4.1 `distribution-imports`

This family maps one selected artifact to import roots it contributes. Its
scope is `{ "artifact": "model" }`. Each fact payload contains `importRoots`,
an unordered non-empty set of absolute module-component arrays. Optional
`namespaceContributions` lists namespace module-component arrays for which the
artifact is one contributor. An import root is a binding fact, not a claim that
all descendants exist.

Facts combine by set union only when artifact selectors, profile version, and
compatibility conditions are identical. Contradictory mappings from the same
exact artifact are a semantic conflict and make the family scope
uninterpretable; source priority MUST NOT choose a winner.

### 4.2 `import-bindings`

This family maps names visible in a module to exact symbols. Its scope is
`{ "module": <symbol-id> }`. Payload `bindings` is an unordered set of objects
with `name`, `bindingKind`, `target`, and optional conditions. A complete claim
licenses absence only for bindings in the exact module, resolved environment,
and condition set named by the scope; it says nothing about submodules,
dynamic attributes, other namespace contributors, or declaration aspects.

Conflicting targets for the same name and overlapping conditions make that
binding uninterpretable unless the producer reports partial/unknown coverage
with a typed limitation explaining unresolved dispatch.

### 4.3 `declaration-correspondence`

This family records evidence-bearing relationships between a declaration
artifact and runtime symbols. Its scope is
`{ "declarationArtifact": "model", "runtimeArtifact": <purl> }`, where the
runtime PURL is canonical and exact-versioned. Payload `mappings` is an
unordered set of `declaration`, `runtime`, and `relation` objects. The
declaration handle resolves in the enclosing declaration-artifact model; the
runtime handle resolves through an explicit symbol definition whose
`artifactSelectors` select the named runtime artifact. Relations are
`describes`, `augments`, or `replaces-for-type-checking`.
They do not assert runtime identity, behavioral equivalence, or completeness.

Mappings combine only for identical declaration and runtime artifact scopes,
conditions, and profile versions. Two mappings that assign incompatible
runtime targets to one declaration are a conflict. Missing runtime artifact,
version, or environment evidence makes correspondence indeterminate.

## 5. Compatibility and conditions

A `csmi.python` compatibility constraint value is an object with any of these
conjunctive fields:

- `python`: an exact version or canonical `vers:generic` range;
- `implementation`: a non-empty set of lowercase implementation identifiers;
- `abi`: a non-empty set of canonical Python ABI tags;
- `platform`: a non-empty set of canonical platform tags;
- `extras`: the unordered set of normalized distribution extras required to be
  enabled; and
- `projectConfig`: an object containing a required `digest` and
  `canonicalization` URI for resolver-affecting configuration.

Python version, implementation, ABI, and platform select where already-chosen
semantics hold. They do not replace identity-bearing PURL qualifiers or
digests. Extras are configuration, not separate distributions. Project
configuration includes import roots, namespace composition, editable installs,
path modifications, type-checker modes, and plug-ins whenever they affect a
fact used by the model. A producer MUST digest such configuration rather than
embed a local path or tool command.

Set-valued implementation, ABI, and platform constraints match when the
candidate supplies one exact member. Extras match only when every required
extra is enabled. Version ranges use the named VERS comparison procedure.
Project configuration matches only with equal digest algorithm, coverage,
canonicalization, and value. All present fields are conjunctive.

Evaluation returns `compatible`, `incompatible`, or `indeterminate` under the
CSMI core. Missing evidence is indeterminate. Unsupported profile semantics
make the affected model uninterpretable. Neither state may be relabeled as
artifact `not matched`.

Conditions inside profile facts use the same field meanings and are
conjunctive. A fact applies only when its conditions are compatible. Overlap or
conflict that a consumer cannot decide is indeterminate and fails closed.

## 6. Completeness and failure behavior

Profile family identity is the tuple `csmi.python`, `0.1.0`, and the family key.
Completeness never crosses that tuple or scope.

- complete `distribution-imports` covers only the selected artifact's direct
  import roots for the exact environment;
- complete `import-bindings` covers only one module's bindings for the exact
  conditions and known namespace contributors; and
- complete `declaration-correspondence` covers only mappings between the two
  named artifact scopes under the exact conditions.

Completeness for a module does not close submodules, a distribution, a
namespace package, a runtime, a stub artifact, or the Python standard library.
Stub completeness does not close runtime declaration records or procedure
summaries. Core completeness does not close these profile families.

Unsupported required profile versions or identity rules make affected facts
uninterpretable. Missing distribution/import mapping, contributor resolution,
stub/runtime correspondence, compatibility evidence, or required dynamic
semantics produces `indeterminate` applicability/compatibility/binding as
appropriate. A contradicted comparable constraint produces `not matched` or
`incompatible`. Malformed payload or a false complete claim is semantically
invalid. None of these outcomes is a complete empty model.

## 7. Reference analyzer mapping

An analyzer may map its resolver-proven absolute module and owner chain to the
descriptor path, and its exact package environment to artifact and compatibility
evidence. For Bifrost, a resolved Python module plus declaration FQN may be an
input to this construction, but the analyzer FQN itself is not the CSMI key.
Its Python import graph may supply `distribution-imports` and `import-bindings`
only where resolution provenance is retained. Stub declarations remain
declaration evidence and typing overloads remain declaration-only; compiled
semantic-pack IDs, source spans, and display strings are not exported as
identity.

This mapping is informative. Bifrost's authored and compiled pack schemas are
not part of this profile, and an independent consumer can implement every rule
above without linking Bifrost.

## 8. Non-goals

This profile does not standardize Python packaging, import execution, the full
typing specification, a type checker, dependency resolution, environment
markers, standard-library contents, third-party APIs, native extension ABIs,
or Bifrost's internal model format. It defines only the portable evidence and
failure boundaries needed to exchange semantic facts safely.
