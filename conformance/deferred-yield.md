# Deferred-yield conformance

These obligations accompany `csmi.deferred-yield` `0.1.0`. This document is a
normative conformance contract; executable schema and structural fixtures are
registered separately and are not defined by this document. Structural
acceptance, semantic validity, artifact applicability, and consumer support
remain separate outcomes.

| Case | Required result |
| --- | --- |
| Exact factory, resume, and handle-type identities | Apply only through a consumer-established handle linking construction to a resume on that handle; matching handle type alone is insufficient. |
| Same display name but different artifact or callable identity | No application. |
| Missing, duplicate, or ambiguous linked-scope endpoint | Reject the fact rather than infer the missing endpoint. |
| Factory construction | Establish a handle retaining an exact collection source; do not transfer an item or synthesize a loop. |
| `retention: "borrowed-shared"` | Preserve other shared access while excluding unsupported exclusive use during the valid period. |
| `retention: "borrowed-exclusive"` | Preserve the exclusive-access distinction; do not represent it as shared or owned. |
| `retention: "owned"` | Preserve the ownership transfer from collection source to the handle relationship. |
| One supported resume call | At most one delivered item. |
| Zero, one, or repeated resumes on one handle | Preserve zero-or-one per call and zero-or-more per handle, including the zero-iteration path. |
| Explicit entry key and value member positions | Bind only proven distinct in-range members to key and value. |
| Two-component product without mapping evidence | Retain unknown or unsupported key/value correspondence; do not infer component 0 is key. |
| Shared-borrow delivery | Preserve the retained source relationship and read-only observation where supported. |
| Exclusive-borrow delivery | Preserve exclusive access and mutation capability without claiming ownership transfer. |
| Move or copy delivery | Distinguish portable ownership transfer from a copied value; neither proves byte-for-byte alias identity. |
| Derived delivery | Retain exact derivation evidence; do not infer equality or an unspecified property. |
| Source-mutation or handle-drop invalidation | Apply the recorded conservative constraint and retain affected uncertainty. |
| `none-asserted` invalidation | Keep unrepresented invalidation open-world; do not infer permanent validity. |
| Unknown or unsupported variant | Preserve its typed limitation; it cannot close a complete scope. |
| Conflicting supported records | Preserve the conflict; input order never selects truth. |
| Complete scope with any unresolved endpoint, mapping, retention, delivery, constraint, or termination obligation | Reject the completeness claim. |
| Unsupported exact required profile version | Affected units are uninterpretable, not empty. |
| Budget exhaustion or cancellation | Preserve typed incompleteness; positive evidence does not certify exhaustiveness. |
| Consumer lowers a yield as an eager during-call transfer | Invalid: construction and later resume must remain distinct. |

The executable suite MUST demonstrate positive and structural-invalid payloads,
shared-retention versus exclusive-delivery and duplicate-member semantic near
misses, complete and partial full-document joins, a rejected complete claim
with unsupported validity, missing affected scope, repeated resumes, and an
empty source. Passing schema validation does not certify production compiler
interoperability.
