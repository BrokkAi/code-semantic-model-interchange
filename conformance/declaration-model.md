# Declaration-model conformance cases

These semantic cases are normative for CSMI 0.1 declarations. Issue #9 will
translate them into fixtures for the normative JSON serialization.

## Valid declaration facts

| Case | Expected interpretation | Reason |
| --- | --- | --- |
| Java static method owned by a type with no receiver | Callable has no input receiver | Ownership does not imply receiver presence. |
| Java instance method with an `instance` receiver | Receiver is separate from position-zero parameter | Receivers are not members of the explicit parameter sequence. |
| Python function with positional-only, named-only, and variadic named parameters | Parameters bind under their declared forms and positions | Language spelling is normalized to portable invocation roles. |
| TypeScript class plus `conforms-to` and member `implements` relationships | Direct contract and member realization are known | Relationships are resolver-proven directional facts. |
| Rust associated function owned by a type with no receiver | Callable is receiver-free | An owner type does not turn an associated function into an instance method. |
| Rust method with an `instance` receiver | Receiver is known without parsing `self` source text | Receiver semantics are explicit. |
| Generic declaration and an application of its declared type to a type argument | One declaration plus a type expression | A use-site instantiation is not a new declaration. |
| Pack omits an unused display name, source kind, or type fact | Remaining facts retain their meaning | Optional metadata and absent facts do not become negative claims. |
| Required declaration aspect is embedded in the applicable pack | Model is self-contained for that aspect | No consumer declaration source is needed. |
| Required aspect has an explicit consumer-resolved dependency and equivalent local evidence | Model is interpretable as supplemented | The dependency and local provenance remain observable. |

## Near misses and fail-closed outcomes

| Pack or source fact | Other evidence | Expected outcome | Reason |
| --- | --- | --- | --- |
| Same callable symbol with `instance` receiver | Local declaration says there is no receiver | Declaration conflict; affected model is uninterpretable | Receiver shape is single-valued and affects port binding. |
| Parameter zero is `positional-only` | Local declaration says parameter zero is `named-only` | Declaration conflict; affected model is uninterpretable | Invocation binding differs. |
| Pack asserts a return type | Local source omits a return-type fact under incomplete coverage | No conflict | Omission is not a negative claim. |
| Pack asserts `A inherits B` | Another source asserts `A conforms-to C` | Both facts may apply | Relationship predicates are multi-valued and not mutually exclusive. |
| Pack asserts `A inherits B` and `B inherits C` | No `A inherits C` triple | Direct `A inherits C` is unknown | Core relationships do not imply transitive closure. |
| Type alias `UserId` targets `String` | Reference to `String` | Symbols remain different | Alias expansion and identity equivalence are not inferred by core. |
| Two type expressions are `unknown` | No additional profile evidence | Equality is unknown | Shared lack of type information is not type equivalence. |
| Callable result type is `unknown` | Equivalent source provides one known result type | Known type refines the unknown | Unknown type evidence does not conflict with known evidence. |
| Required consumer-resolved shape | Consumer has no declaration for the symbol | Affected model is uninterpretable | Required declaration evidence is unavailable. |
| Consumer declaration uses an unsupported symbol scheme | Encoded descriptor text happens to match | Affected model is uninterpretable | Local data cannot repair unsupported identity semantics. |
| External type reference | Artifact identity and symbol scheme are comparable, but no behavioral model for that artifact is selected | Type identity remains usable | External type identity does not require applying external behavior. |

## Equivalent and conflicting merges

| First source | Second source | Expected outcome |
| --- | --- | --- |
| Declaration category and callable shape | Exact duplicates for the same symbol | Equivalent facts; one semantic assertion. |
| Complete declaration record | Additional display name only | No semantic conflict. |
| Declaration with no owner fact | Same symbol with an owner fact | Merge the asserted owner; omission alone is not conflict. |
| `implements` relationship | Exact duplicate including type arguments | One relationship fact. |
| Two different `conforms-to` objects | Both resolver-proven | Two relationship facts, not a conflict. |
| One type-alias target | Different type-alias target for the same symbol | Conflict. |
| One atomic callable shape | Different parameter count, order, binding, receiver, or result shape | Conflict. |

An internal conflict between embedded facts is semantic invalidity. A conflict
between a valid embedded fact and consumer-resolved local evidence makes the
affected model uninterpretable; a consumer must not choose a winner.

## Invalid declaration models

Each of these is semantically invalid rather than merely incomplete:

- more than one declaration record for the same symbol in one semantic model;
- a portable declaration category incompatible with the symbol's terminal
  descriptor role under its identity scheme;
- an owner from a different artifact identity scope;
- a value parameter not owned by its callable;
- a type parameter not owned by the declaration that lists it;
- duplicate, negative, or non-contiguous parameter or result positions;
- a `positional-or-named` or `named-only` parameter without a
  resolver-significant label;
- a receiver repeated as an explicit value parameter;
- a present callable shape that omits an explicit parameter or logical result;
- a `type-alias` declaration without one alias target;
- an `inherits` or `conforms-to` relationship whose endpoints are not types;
- an `overrides` or `implements` relationship with incompatible member
  categories;
- a relationship inferred only from equal display names or source text;
- a required declaration-defined aspect with neither an embedded fact nor an
  explicit consumer-resolved dependency; or
- silently using local declarations without establishing artifact
  applicability, scheme support, aspect equivalence, and supplemented
  provenance.
