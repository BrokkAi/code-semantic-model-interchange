# CSMI v0.1 fixtures

The fixture groups exercise different conformance boundaries:

- `valid/` contains structurally valid representative documents with no
  intentionally embedded semantic violation. Manifest resource bytes are not
  materialized by these standalone schema fixtures.
- `invalid/` contains structurally invalid documents. Every file must be
  rejected by `spec/0.1/schema.json`.
- `semantic-invalid/` contains documents that intentionally pass JSON Schema
  but violate a named semantic invariant from the specification.
- `profile-inputs/` contains canonical inputs whose derived profile identities
  are recomputed and matched to serialized valid-fixture symbols.

The semantic-invalid group is important: successful core JSON Schema validation
establishes structure only. It does not resolve symbol references, prove
artifact applicability, establish profile support, or license closed-world
inference. For repository-owned standard profiles, the validation script also
validates recognized payloads in valid documents against their exact declared
profile schemas. Standalone schema fixtures use synthetic digest values where
resource bytes are intentionally not materialized; they are shape and semantic
invariant evidence, not proof of those external artifacts. Derived TypeScript
signature digests are the exception and are recomputed from `profile-inputs/`.

Run all structural fixture expectations with:

```sh
python3 scripts/validate-schema.py
python3 scripts/validate-profiles.py
```

Versioned profile payload schemas and their focused fixtures live under
`profiles/<name>/<version>/`. Profile schema acceptance remains distinct from
the semantic conformance cases under `conformance/`.

The Java/JVM family uses four independently versioned payload schemas and keeps
its structural and semantic cases under `fixtures/profiles/java-jvm/`. These
profile-owned schemas do not add language-specific fields or identity rules to
the language-neutral core schema.
