# Value-transfer conformance cases

These cases are normative for `csmi.value-transfer` `0.1.0`.

| Case | Expected result | Reason |
| --- | --- | --- |
| Core transfer carries a copy attachment | Distinct destination identity | The core locations are the endpoints; no duplicate handles are invented. |
| Copy followed by mutation of the source | Destination retains the transferred value | Copy does not alias source storage. |
| Reference, pointer, or shared backing-store binding | No transfer attachment | Storage identity is shared or a pointer value, not the referenced object value. |
| Exact `std::basic_string` copy constructor selected | `operation: implicit` with its local symbol | Structured owner/member evidence selects the operation. |
| Custom same-named class or wrong overload | No optimistic exact operation | Names and rendered signatures are not portable identity. |
| Type copy aspect uses its exact copy-constructor member | Conforming type fact | Scope, owner, and implicit-operation role agree. |
| Type copy aspect names a copy-assignment member | Semantically invalid | Assignment does not prove type-wide copy construction. |
| Conversion reports `changing` | Value dependence remains, identity preservation does not | Preservation is explicit and cannot be strengthened. |
| Move reports unknown invalidation | Preserve `unknown` | Consumers cannot assume invalidation or source preservation. |
| Unresolved operation reports a typed limitation | Usable uncertain attachment under unknown or partial identity-separating-transfer coverage | No declaration identity is fabricated. |
| Complete type-aspect scope contains unknown behavior | Semantically invalid | A known semantic gap contradicts complete coverage. |
| Complete implicit-operation scope contains two distinct members | Complete two-element set | Completeness does not manufacture uniqueness. |
| Required profile is unsupported by a consumer | Uninterpretable | Structural payload validation is not executable support. |

Complete core procedure-summary coverage closes only core transfers for that
callable. It neither closes the profile's identity-separating classification
nor says anything about aliases, mutation, heap effects, exceptions, escape,
or another profile family.
