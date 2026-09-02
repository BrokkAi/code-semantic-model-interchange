# Reference mapping: CSMI JavaScript/TypeScript/Node to Bifrost

This non-normative mapping demonstrates how one analyzer can compile the
normative profile without making its native pack model part of CSMI. It targets
the public Bifrost semantic-model surfaces current when this mapping was
written: `JsTsDependencyPackAdapter`, `AuthoredProcedureTarget`,
`AuthoredProcedureSummary`, and `ProcedureSummaryTargetKey`.

The adapter is a semantic boundary, not a field-copying recipe. It first
validates CSMI core and both exact profile versions, establishes every artifact
match and compatibility result, and binds descriptor paths through Bifrost's
JavaScript/TypeScript resolver. It stops with an unsupported, indeterminate, or
uninterpretable result before producing a native pack when those proofs fail.

## Activation

| CSMI input | Bifrost native destination | Required proof |
| --- | --- | --- |
| npm artifact selector | shard `activation.package` | Canonical npm PURL converts to the exact package name/version; any digest is preserved as activation evidence. |
| Node distribution selector | Node-runtime activation context | Exact generic PURL and required official archive digest both match. |
| `node-runtime` constraint | toolchain/runtime compatibility | Structured SemVer interval, platform, and architecture are supported and compatible. |
| `node-module-resolution` | JavaScript/TypeScript resolver context | Module system, export key, active conditions, and selected-target digest all match. |
| `typescript-resolution` | `JsTsDependencyPackAdapter` context | Compiler interval, resolution/module modes, conditions, JSX mode, and effective-options digest agree. |

Bifrost must preserve an indeterminate selector or compatibility comparison as
an incomplete activation outcome. It must not compile a dormant pack whose
absence later looks like a complete empty model.

## Symbols and declarations

For `csmi.javascript-runtime`:

- the first namespace descriptor becomes the resolver's canonical external
  module/export owner (`node:child_process` for the fixture);
- the terminal callable descriptor becomes the resolver-proven export binding
  (`execSync`);
- callable shape supplies `has_receiver`, fixed parameter count, and variadic
  status; and
- the adapter retains the complete CSMI symbol key alongside any compact native
  IDs used for caching and diagnostics.

The fixture therefore maps to a Bifrost `AuthoredProcedureTarget` equivalent to
`path = "node:child_process"`, `symbol = "execSync"`, `has_receiver = false`,
and `parameter_count = 2`. Those strings are safe only because the adapter has
already proven the full CSMI artifact, profile, descriptor, and resolver
identity. A Bifrost loader that searches every call named `execSync`, accepts an
unresolved module string, or drops the activation proof is not this mapping.

For `csmi.typescript-declaration`, the adapter routes exact declaration
artifacts through `JsTsDependencyPackAdapter`. Type-space and value-space
symbols remain separate. A `tsig-0.1` overload key is retained as declaration
identity even when Bifrost's current runtime procedure-summary index needs only
the single JavaScript runtime binding. If a future native declaration fact
cannot preserve that overload identity, import stops as unsupported instead of
collapsing overloads by name and arity.

## Procedure summaries

Each applicable CSMI core summary becomes one Bifrost
`AuthoredProcedureSummary`:

- CSMI callable handle -> the bound `AuthoredProcedureTarget` above;
- input `parameter[n]` -> native summary input parameter ordinal `n`;
- normal `result[0]` -> native normal-return output;
- CSMI transfer set -> native `transfers` set; and
- callable-scoped CSMI `procedure-summaries` status -> native summary
  `completeness` for that exact target only when the status is `complete`;
  otherwise the native representation must retain the partial/unknown limit.

The `execSync` fixture's single transfer compiles to parameter ordinal `0` ->
normal return with partial coverage. The mapping does not infer process
execution, I/O, invocation, throwing, mutation, taint behavior, or any absent
transfer from that illustrative edge.

## Runtime/declaration mappings

`runtime-declaration-bindings` is stored as an adapter-side association between
the exact runtime symbol key and exact declaration symbol keys. Bifrost may use
it to connect resolved TypeScript call sites to the runtime summary. It is not
lowered to symbol equality, an authored procedure target, or a completeness
claim about either artifact.

When the `@types/node` selector is not matched, TypeScript compatibility is
indeterminate, or the mapping family is unsupported, the adapter does not use
the declaration relation. The independently applicable runtime summary may
remain usable only if its required affected boundary proves that it does not
depend on that mapping.

## Completeness and diagnostics

The adapter preserves family boundaries:

- core procedure-summary completeness maps only to the native procedure
  summary;
- declaration-mapping completeness remains adapter metadata and never becomes
  native procedure-summary completeness; and
- partial/unknown, unsupported, conflict, inapplicable, and indeterminate
  outcomes remain separately diagnosable.

Native pack compilation, catalog storage, cache keys, and runtime indexes are
Bifrost implementation details. Another consumer can use different structures
while assigning the same CSMI meaning.
