# Symbol identity conformance cases

These semantic cases are normative for CSMI 0.1 symbol identity. Issue #9 will
translate them into fixtures for the normative JSON serialization.

## Equal identities

| Left | Right | Expected outcome | Reason |
| --- | --- | --- | --- |
| Same artifact, scheme version, stability, and descriptor path | Independently produced equivalent key | `same` | Every identity component agrees under the scheme. |
| Java overloaded method key | Same method with a different display name | `same` | Display metadata is not identity. |
| Generated declaration | Equivalent key classified with different origin metadata | `same` | Origin does not override scheme-defined identity. |
| Generic Rust function declaration | Reference using the same declaration key with `T = String` in a type expression | `same` | A use-site instantiation is not a new declaration. |

## Near misses and indeterminate identities

| Left | Right | Expected outcome | Reason |
| --- | --- | --- | --- |
| Same descriptor path in two distinct artifact identity scopes | Same path | `different` | Artifact scope is part of the symbol key. |
| Same artifact and descriptor path under `java-source` | Path under a supported `jvm-binary` scheme | `different` | Scheme identity is part of the key even when both schemes are understood. |
| Same artifact, scheme, and descriptor path under scheme version 1 | Path under supported scheme version 2 | `different` | A scheme version selects its identity and comparison rules. |
| Java `normalize(String)` | Java `normalize(byte[])` | `different` | Scheme-defined callable disambiguators differ. |
| Java `foo(int, int)` | Java `foo(Integer, int)` | `different` | Boxing does not erase resolver-visible overload identity. |
| Constructor | Same-signature static factory or initializer | `different` | Callable kind and normalized scheme name distinguish the declarations. |
| Python nested `normalize` | Same simple name under another function | `different` | The enclosing descriptor path differs. |
| TypeScript instance method | Same display name for a static method | `different` | The scheme must distinguish their declaration identities. |
| TypeScript type named `Result` | Value or namespace named `Result` in the same module | `different` | The scheme must preserve distinct declaration spaces. |
| JavaScript export `normalize` from module A | Same local/export name from module B | `different` | The module descriptor differs. |
| Rust inherent method | Same name from a trait implementation | `different` | Ownership and implementation path differ under the Rust scheme. |
| Supported key | Key using an unsupported scheme version | `indeterminate` | The consumer cannot apply the scheme's comparison rules. |
| Artifact-local key | Same encoded key without exact artifact evidence | `indeterminate` | Artifact-local identity requires exact content scope. |

## Invalid symbol keys

Each of these is semantically invalid rather than indeterminate:

- an empty descriptor path;
- an identity scheme without a version;
- a compound FQN stored as one descriptor instead of an enclosing path;
- sibling descriptors that collide under the scheme but lack a disambiguator;
- an overload ordinal or source order used as the sole portable disambiguator;
- a display name or analyzer FQN used as the symbol key without an identity
  scheme defining its construction;
- an artifact-local key with any alternative artifact selector that lacks
  required exact-content digest evidence;
- an artifact-local identity based only on source offsets;
- a document-local external ID referenced outside its defined scope without a
  valid artifact-local mapping;
- a PURL `subpath` used as a substitute for symbol descriptors;
- a use-site generic instantiation minted as a declaration without a
  scheme-defined specialization; or
- a local or anonymous entity assigned an unstable ID instead of being reported
  as omitted under completeness.
