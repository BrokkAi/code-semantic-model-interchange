# Effects, profiles, and extensions conformance cases

These semantic cases are normative for CSMI 0.1 vocabulary uses. Structural
serialization cases live under `fixtures/`; this table defines the additional
vocabulary checks that JSON Schema cannot prove.

## Namespace and version cases

| Case | Outcome | Reason |
| --- | --- | --- |
| CSMI assigns `csmi.effects.mutation` in a future standard profile | Valid standard-profile identifier | Only CSMI governance may assign the reserved prefix. The name alone does not make support mandatory. |
| Publisher controlling `brokk.ai` defines `ai.brokk.bifrost.generator-rules` | Valid vendor-extension identifier | The leading labels are the publisher's reverse-DNS authority. |
| A producer defines `brokk.bifrost.generator-rules` | Semantically invalid | A bare product prefix is collision-prone and does not establish namespace authority. |
| A distributable pack defines an `example.*` or `org.example.*` vocabulary | Semantically invalid | Those prefixes are reserved for examples and conformance fixtures. |
| Consumer supports version `1.2.1` while the use declares `1.2.0` | Unsupported unless an implemented normative compatibility rule covers it | SemVer resemblance or precedence is not CSMI compatibility evidence. |
| Payload schema has an absolute RFC 3986 URI and validates under JSON Schema Draft 2020-12 | Structurally valid payload only | Schema validation does not prove semantic support. |
| Consumer fetches and executes an unknown schema to infer semantics | Non-conforming interpretation | A schema URI is an identifier, not executable authorization or a semantic plug-in. |

## Required and optional uses

| Case | Outcome | Reason |
| --- | --- | --- |
| Unsupported optional family is removed and every core and supported-profile result remains identical | Unaffected semantics remain interpretable | This is the required test for an optional use. The unsupported family itself is not interpreted. |
| Unsupported optional payload is preserved by a proxy | Conforming round trip | Preservation does not claim semantic support. |
| Unsupported required family names one callable scope | That family scope and its dependents are uninterpretable | Unrelated core facts remain usable when the affected boundary proves independence. |
| Unsupported required projection scheme appears in a core transfer | The transfer is uninterpretable | Dropping the projection would change its location meaning. |
| Producer marks a profile optional even though dropping it changes completeness or negative inference | Semantically invalid declaration | Completeness-changing uses are required semantics. |
| Required use omits its affected family, core fact, or attachment target | Semantically invalid declaration | A consumer cannot determine the fail-closed boundary. |
| Consumer silently downgrades a required use to optional | Non-conforming interpretation | Requiredness is producer-declared semantic evidence, not a consumer preference. |
| Unknown extension data has no declared vocabulary use | Semantically invalid | Requiredness, version, schema, and affected scope cannot be established. |

## Extension surfaces and effect families

| Case | Outcome | Reason |
| --- | --- | --- |
| Vendor profile defines a namespaced mutation family scoped to one exact callable | Permitted extension family | The profile must define target, modality, equality, conflict, merging, and completeness. |
| Profile supplies a value at a core-delegated projection-scheme slot | Permitted delegated vocabulary | The core specification explicitly delegates the slot and unsupported required use fails closed. |
| Profile adds namespaced data at a schema-defined attachment point | Permitted attachment | Its target identity, affected boundary, and removal behavior must be defined. |
| Taint or effect profile uses an unindexed receiver root and `parameter[n]` for a named parameter's declaration position | Valid profile operands | Profiles may reuse core boundary locations; receiver remains first-class and named-call syntax does not change parameter identity. |
| Extension adds an arbitrary `mutation` property directly to a core procedure summary | Structurally invalid under the closed core schema | Extensions do not create an open-object escape hatch. |
| Producer emits core `{ "effect": "mutation" }` | Semantically invalid core fact | CSMI 0.1 defines no generic core effect vocabulary. |
| Mutation fact is inferred from a core parameter-to-receiver transfer | Incorrect interpretation | Information transfer and mutation are independent unless a vocabulary use declared `required` defines their relationship. |
| Complete empty core procedure-summary set is treated as no mutation or invocation | Incorrect interpretation | Core transfer completeness never closes a profile-owned effect family. |
| Complete profile mutation family is treated as global purity | Incorrect interpretation | The claim closes only that exact family, version, and scope. |
| Facts from two profile versions are merged because their payload keys match | Non-conforming aggregation | Exact versions are incomparable without an implemented normative mapping. |
| One vocabulary version defines mutation and escape families but omits stable family keys | Semantically invalid family definitions | Family identity is the vocabulary identifier, exact version, and family key tuple. |

## Bifrost generator guidance

| Case | Outcome | Reason |
| --- | --- | --- |
| Generator family uses `ai.brokk.bifrost.generator-rules`, exact callable and declaration symbols, and core boundary locations | Portable vendor-extension shape | Namespace authority and resolver-proven identities are explicit. |
| Generator rule identifies a target by display name, regex, source text, or producer database ID | Non-portable and semantically invalid for interchange | Textual resemblance and local IDs do not establish CSMI identity. |
| Vendor generator family is renamed in place to a `csmi.*` profile | Invalid promotion | Standardization requires a new assigned identifier or normative mapping plus independent conformance evidence. |

## Interoperability obligations

A producer and consumer claiming support for a vocabulary version must agree on
its namespace authority, schema identity, semantic rules, dependencies,
attachment points, affected-unit grammar, fact-family operations, and
completeness behavior. Structural preservation of an unknown payload is useful
but is not semantic support.

Unsupported optional data may be isolated. Unsupported required semantics,
malformed affected boundaries, version mismatches, and cross-version conflicts
must remain observable and must never be flattened into inapplicability,
unknown coverage, or a complete empty set.
