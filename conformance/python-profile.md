# Python profile conformance cases

These cases are normative for `csmi.python` `0.1.0`. Profile payload fixtures
live under `profiles/python/0.1/fixtures/`; complete CSMI documents live under
the repository-level `fixtures/` tree.

## Identity and binding

| Case | Outcome | Reason |
| --- | --- | --- |
| `beautifulsoup4` distribution maps by proven metadata to import root `bs4` | Valid mapping | Distribution and import identity are explicitly related rather than inferred. |
| A producer changes `beautifulsoup4` to `beautifulsoup4` and derives that as the import root | Semantically invalid | PEP 503 normalization does not construct Python imports. |
| Two namespace contributors map to `google.cloud` in the same resolved environment | Distinct artifact-scoped keys contribute to one resolved binding view | Descriptor paths agree, but core artifact scope remains part of identity. |
| `import x as y` and a resolved use of `y` target `x` | Same target symbol | Alias spelling is a binding, not another target identity. |
| `pkg.__init__` re-exports `impl.Widget` as `Widget` with resolver evidence | Valid `re-export` binding | The exported name points to the exact target. |
| Equal import text resolves to different modules under two project configurations | `indeterminate` until configuration is established | Text and path-search guesses cannot select identity. |
| Nested `outer.inner` declaration versus a module-level `inner` | Different | Resolver-established owner descriptors differ. |

## Runtime, stubs, overloads, and descriptors

| Case | Outcome | Reason |
| --- | --- | --- |
| Inline `.pyi` declaration explicitly corresponds to a runtime function | Valid `describes` mapping | The relationship is evidence-bearing and symbol-scoped. |
| `types-requests` distribution is treated as the `requests` runtime artifact | Semantically invalid | Stub and runtime artifacts have distinct selectors. |
| Same name and descriptor text occur in stub and runtime artifacts without correspondence | Indeterminate correspondence | Resemblance is not identity or mapping evidence. |
| Two `@overload` variants use distinct canonical signature disambiguators | Distinct declaration-only callables | Typing variants are not runtime dispatch targets. |
| Runtime implementation receives an overload signature disambiguator | Semantically invalid | Python runtime dispatch does not select typing overloads. |
| Property `value` has child callables `get` and `set` | Three distinct symbols | The term and independently invocable accessors have separate roles. |
| Decorator returns the original callable and resolution proves the binding | Same callable identity | Decorator syntax alone is irrelevant; binding proof controls. |
| Decorator replaces a function with an unrelated callable | Binding targets the replacement | Equal display names do not equate declarations. |
| Module `__getattr__` may supply `dynamic_name` but no stable binding is proven | Omitted with partial/unknown coverage | Dynamic availability is not portable identity. |
| Generated class is deterministically import-visible in every applicable artifact | Portable generated declaration | Origin does not determine stability. |

## Applicability and compatibility

| Artifact and evidence | Outcome | Reason |
| --- | --- | --- |
| `pkg:pypi/beautifulsoup4@4.13.0`, matching runtime, and proven `bs4` mapping | Applicable | Artifact identity and import mapping independently agree. |
| Matching PyPI artifact, but required extra `security` is not enabled | `incompatible` | Extras constrain the environment after artifact selection. |
| Matching artifact and no evidence about required project configuration digest | `indeterminate` compatibility | Missing evidence is not contradiction or a match. |
| CPython stdlib selector evaluated against PyPy | `not matched` | The identity-bearing implementation qualifier is contradicted. |
| CPython stdlib selector matches, but platform evidence for `_winapi` is absent | `indeterminate` compatibility | Availability cannot be inferred from another platform. |
| Consumer understands core CSMI but not required `csmi.python` `0.1.0` | Affected model uninterpretable | Opaque payload preservation is not profile support. |
| Consumer supports `csmi.python` `0.2.0` only | Version `0.1.0` unsupported | Similar or newer-looking versions are not comparable without a normative mapping. |

## Completeness and near misses

| Claim | Outcome | Reason |
| --- | --- | --- |
| Complete `import-bindings` for `requests` under an exact environment | Absence may be inferred only for that module and condition scope | Submodules and dynamic attributes remain open. |
| Complete `.pyi` correspondence is used to assert complete runtime declarations | Non-conforming inference | Declaration evidence does not close runtime facts. |
| Complete `google.cloud` bindings omit an unresolved namespace contributor | Semantically invalid complete claim | All relevant contributors are required inputs. |
| Unsupported dynamic attributes are omitted with partial coverage and `unsupported-semantics` | Valid fail-closed result | Unavailable identity remains observable. |
| Empty import-binding facts under unknown coverage are reported as no exports | Non-conforming interpretation | Empty partial evidence is not absence. |
| Complete callable procedure summary is generalized to its distribution | Non-conforming inference | Core callable scope does not close a module or distribution. |

## Independent-consumer algorithm

A conforming consumer can implement the profile without producer-specific
state: validate both schemas; establish artifact applicability; evaluate the
required profile use and compatibility; compare descriptor paths exactly;
resolve each binding and correspondence by local symbol ID; retain family and
scope on completeness; and emit `uninterpretable` or `indeterminate` at the
first unsupported or missing required boundary. The valid fixture is a
machine-readable demonstration of that algorithm. No Bifrost field or ID is
required.
