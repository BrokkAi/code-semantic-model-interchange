# Runtime exposure and keyed-read value conformance cases

These cases are normative for `csmi.runtime-values` `0.1.0`. Structural validity, semantic validity, runtime applicability, and consumer interpretability are evaluated independently.

## Positive observations

| Case | Expected outcome |
| --- | --- |
| JavaScript `process.env.DFB_INPUT` under one exact enabled Node main-realm profile, with complete lexical/rebinding proof | Exact property/load/result identity and full expression correspondence; input origin is exact only if mutation coverage is complete. |
| JavaScript `process.env["DFB_INPUT"]` under the same contract | Same decoded property identity; bracket source form remains distinct. |
| JavaScript `process.argv[2]` | Exact numeric index and terminal indexed-load result; no assertion that index 2 exists. |
| TypeScript annotated env read | Same runtime observation when binder and mapping evidence are independently complete; annotation adds no runtime proof. |
| TSX read used inside JSX | Full source expression ends at the keyed read, not the enclosing JSX expression. |
| Selected key overwritten before read | Exact access identity may remain, but `sourceOrigin` is `mutated`, not pristine input. |

## Conclusive exclusions and incomplete near misses

| Case | Required result |
| --- | --- |
| Parameter, local, import, catch, function, class, or value-space TypeScript binding named `process` | Conclusive lexical exclusion; no runtime-global observation. |
| Nested shadow binding and assignment beside an otherwise proven global read | The nested write does not poison the global; scopes remain distinct. |
| Unbound `process = fake`, destructuring/update/loop writes, or proven `globalThis.process` replacement | Rebinding present; no exact pristine global binding. |
| Missing, disabled, incompatible, or conflicting exposure | Respectively nonmatching, indeterminate, or conflict; never an empty exact model. |
| Node typings with no exact runtime activation | Indeterminate activation; declarations do not expose a runtime global. |
| `env[key]`, `argv[i]`, `argv[1+1]`, negative/fractional/oversized indices, `argv["2"]`, or optional chaining | Dynamic or unsupported key/access semantics; no exact keyed observation. |
| Unknown call, descriptor/getter, proxy, prototype change, `eval`/`with`, preload, native effect, or async boundary | Relevant mutation, accessor, exception, or execution coverage remains partial/unknown. |
| Cancellation, budget exhaustion, stale materialization, or ambiguous load/result join | Typed partial/indeterminate result; no complete reusable observation. |

## Negotiation and round trip

A consumer supporting only core or `csmi.javascript-typescript` cannot interpret `csmi.runtime-values`. It preserves or refuses the required records; it cannot reinterpret them as declaration members or drop them and infer a complete negative. A lossless round trip preserves dot/bracket source form, property/index type, full expression range, load/result/point/phase, activation digests, provenance, limitations, and all unsupported or indeterminate outcomes.
