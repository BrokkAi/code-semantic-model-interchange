# Manifest, provenance, and canonicalization conformance cases

These semantic cases are normative for CSMI 0.1 packs. Issue #9 will define
their concrete JSON serialization and structural fixtures.

## Document and manifest boundaries

| Case | Outcome | Reason |
| --- | --- | --- |
| Semantic document identifies its semantic-model, serialization, and schema versions | Self-describing document | Pack metadata is not required to choose the document's semantics or validator. |
| Versions appear only in the pack manifest | Invalid semantic document | A detached document cannot be interpreted safely. |
| Manifest duplicates a completeness or required-vocabulary summary as authoritative | Semantically invalid pack design | The affected fact family and scope remain the sole semantic source of truth. |
| Standalone valid semantic document has no manifest | Usable semantic input, but not a v0.1 distributable pack | Packaging adds integrity and licensing without changing meaning. |
| Manifest has no `semantic-document` resource | Semantically invalid pack | A resource collection without semantic content is not a CSMI pack. |

## Provenance and assembly

| Case | Outcome | Reason |
| --- | --- | --- |
| Source analyzer records stable producer URI, exact version, target identity, and source digest | Valid source-analysis provenance | The record identifies the producer and material evidence boundary. |
| One default provenance genuinely applies to every fact and claim | Valid shorthand | Every unannotated unit resolves to the same record. |
| Mixed-origin document uses one false default and loses individual origins | Semantically invalid provenance | Composition must preserve the producers that established each fact and claim. |
| Assembler packages existing bytes and records only assembler identity in the manifest | Valid assembly | Selecting bytes does not make the assembler their semantic producer. |
| Assembler rewrites a semantic claim but records only assembly | Semantically invalid provenance | Semantic rewriting is composition and needs document provenance. |
| Composition names exact predecessor document or pack digests and retains original provenance | Valid composition | Derivation and original semantic origin remain distinct. |
| Manual model records a stable reviewed-process identifier and exact revision but no person or timestamp | Valid manual-authoring provenance | Reproducible process identity is required; personal data and wall time are not. |
| Complete source-derived claim cites only a mutable branch, URL, or package coordinate | Non-conforming producer | Inputs materially justifying completeness need exact content evidence. |
| Consumer prefers a newer producer or generation method during conflict | Non-conforming merge | Provenance informs external trust policy, not semantic precedence. |

## Resource descriptors and paths

| Case | Outcome | Reason |
| --- | --- | --- |
| Relative NFC path has no empty, `.` or `..` segment and exact descriptor is unique | Valid logical path | It can be resolved within a pack boundary. |
| Path is absolute, drive-prefixed, backslash-separated, percent-encoded traversal, or contains NUL | Semantically invalid descriptor | A consumer must not guess a safe platform interpretation. |
| Two descriptors use the same path | Semantically invalid manifest | Path resolution would be ambiguous. |
| Two paths intentionally describe identical digest bytes | Permitted | Digest identity does not require one storage path. |
| Semantic reference uses a filename or descriptor array position as symbol identity | Semantically invalid reference | Cross-document semantics use CSMI identities, not packaging layout. |
| Descriptor media type contradicts parsed resource type | Structural or semantic invalidity | File extension or successful parsing must not override the declared type. |
| Vocabulary-schema descriptor binds an absolute URI equal to the schema's top-level `$id` | Valid local schema binding | A consumer can resolve the named schema to integrity-checked bytes without a network fetch. |
| Two schema resources bind the same identifier, or the bound `$id` differs | Semantically invalid manifest | Schema identity must resolve unambiguously by exact value. |
| Resource license is absent | Inherit pack default | Licensing remains deterministic. |
| Custom `LicenseRef` resolves to exactly one bound `license-text` descriptor | Valid custom-license binding | The manifest identifies the corresponding text unambiguously. |
| `LicenseRef` has no binding or more than one binding | Semantically invalid licensing envelope | Custom license meaning is unavailable or ambiguous. |
| Schema or custom-license binding appears on the wrong resource role | Semantically invalid descriptor | Binding meaning depends on the resource's declared role. |
| Pack license is treated as the modeled dependency's license | Incorrect interpretation | The manifest licenses pack resources only. |

## Canonicalization and content identity

| Case | Outcome | Reason |
| --- | --- | --- |
| Root manifest and JSON resources are RFC 8785 JCS bytes after semantic-set normalization | Canonical v0.1 JSON | The same normalized data obtains the same content bytes. |
| JSON object repeats a member name | Invalid I-JSON and invalid pack content | Last-key-wins behavior is not interoperable. |
| Ordered parameter or projection-step array is sorted as a set | Semantically incorrect canonicalization | Ordered sequences preserve their defined order. |
| Set-valued facts appear in different input order | Same canonical order after sorting entry JCS bytes | Presentation order has no semantic meaning. |
| Byte-identical duplicate set entry appears twice | Remove the duplicate before serialization | Exact duplicate set membership has no multiplicity. |
| One fact semantically subsumes another and the canonicalizer drops it | Non-conforming canonicalization | Subsumption is not byte equality and may affect precision or provenance. |
| Profile array has no declared ordered-or-set classification | Semantically incomplete profile serialization | Generic canonicalization cannot guess array meaning. |
| Consumer reparses and reserializes non-canonical resource bytes before digest comparison | Non-conforming integrity check | The descriptor commits to exact supplied bytes. |

## Integrity, signatures, and transport

| Case | Outcome | Reason |
| --- | --- | --- |
| Manifest digest and every resource size and SHA-256 match | Internal byte integrity established | This does not authenticate the source or prove semantic correctness. |
| Expected pack digest differs | Integrity failure; apply no part of the pack | The supplied root is not the requested pack. |
| One resource is missing or has a size or digest mismatch | Integrity failure; apply no part of the pack | A manifest commits to the complete resource set. |
| Consumer maps integrity failure to `partial`, `unknown`, inapplicable, or empty | Non-conforming outcome | Integrity is independent from coverage and applicability. |
| Manifest embeds its own digest | Invalid self-reference | Pack identity is computed externally from canonical manifest bytes. |
| Signature over the same pack is included inside that pack | Invalid same-subject layering | Adding a signer would change the signed subject. |
| Detached attestation names the pack digest and authenticates its payload type | Compatible future layering | Trust evidence can evolve without changing pack identity. |
| Valid signature promotes completeness or makes an unsupported profile interpretable | Non-conforming interpretation | Authentication does not change semantic claims or capabilities. |
| Directory and OCI transports preserve identical logical bytes | Same pack digest | Transport is not pack identity. |
| Archive compression or registry tag is used as content identity | Non-conforming transport | Mutable or encoding-specific location cannot replace digest verification. |

## Interoperability obligations

Consumers must verify the root and every described resource before applying any
semantic fact. They must preserve semantic producer provenance separately from
pack assembly, publication, signing, artifact applicability, vocabulary
support, completeness, and trust policy.

Producers must make JSON set ordering deterministic without changing ordered
semantic sequences. Transport implementations remain responsible for safe,
bounded materialization even though v0.1 does not standardize an archive or
registry protocol.
