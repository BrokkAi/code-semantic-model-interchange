# C and C++ profile conformance cases

These cases are normative for `csmi.c-cpp-resolution`, `csmi.cpp`, and
`csmi.cpp.declaration` version `0.1.0`. The resolution vocabulary applies to C
and C++; alias, template, and special-member semantics apply only to C++.
JSON Schema checks payload shape; the dedicated validator and this document
define semantic outcomes that JSON Schema cannot establish.

## Positive cases

| Case | Expected outcome | Reason |
| --- | --- | --- |
| Two producers resolve the same exact header artifact and the `std` namespace primaries `basic_string/3`, `char_traits/1`, and `allocator/1` | Same declaration keys | Exact artifact scope and resolver ownership agree. |
| `std::string` resolves to `std::basic_string<char, std::char_traits<char>, std::allocator<char>>` | One valid alias fact | The alias target is a closed structured type tree with full declaration keys. |
| Copy initialization selects `basic_string(const basic_string&)` | Exact copy-constructor key | The canonical signature has one const lvalue self parameter and no receiver. |
| Copy assignment selects `basic_string::operator=(const basic_string&)` | Exact copy-assignment key | The canonical signature includes its lvalue self receiver and lvalue self result. |
| A non-const by-value `basic_string` parameter is returned by value | Exact move-constructor key may support a `csmi.value-transfer` invalidating move | The parameter arm of C++ implicit move, exact owner, and unique move member are proven at native commit `8a724c2d2e9975831519b6cdbda0d38ee00dd203`. |
| Copy is followed by mutation of the source object | Copied value remains distinct | The `csmi.value-transfer` copy attachment supplies the identity-separating meaning; this profile identifies the selected declaration. |
| A reference or pointer is initialized from a string object | Alias only, not a copy operation | Storage/value aliasing is not an identity-separating value transfer. |

## Near misses and indeterminate cases

| Case | Required outcome |
| --- | --- |
| `custom::basic_string` has the same terminal name and copy-shaped constructor | Different declaration; no standard copy fact. |
| `std::basic_string<char, custom_traits<char>, std::allocator<char>>` | Different specialization; not the canonical `std::string` target. |
| Copy-shaped `operator=` returns `void` | Different signature; it is not copy assignment under this profile. |
| Candidate takes `basic_string&&` | Exact move-constructor identity when the remaining resolver evidence agrees; never either copy identity. |
| Candidate takes `int` or another class type | Value-changing conversion or unrelated overload; no copy identity. |
| Candidate is found only by rendered signature, source text, or a generated native id | Unresolved for portable purposes. |
| Two exact candidates remain after resolution | Conflict; do not select by declaration order. |
| Direct header is known but transitive closure is partial | Applicability is indeterminate; dependent facts do not apply. |
| Header PURL matches but exact content digest is absent | Artifact applicability is indeterminate. |
| Consumer lacks exact `csmi.cpp` `0.1.0` support | Dependent facts are uninterpretable. |
| C consumer supports `csmi.c-cpp-resolution` but not `csmi.cpp` | Resolution context may be interpreted; C++ alias and special-member facts remain uninterpretable. |
| Named local is returned by value where NRVO may apply | Transfer identity remains incomplete; do not force copy or move. |
| Const by-value parameter is returned | No invalidating move; preserve typed return-transfer incompleteness. |

## Invalid cases

The following are semantically invalid:

- a portable C++ declaration key without exact-content artifact selectors;
- a namespace, template primary, alias, or callable key constructed from
  source spelling without resolver proof;
- an alias target containing a local handle, rendered type, or producer id in
  place of a full declaration key;
- a `cppsig-0.1` suffix that does not hash its attached canonical signature;
- a copy constructor signature with a receiver or result field, non-const
  source, rvalue source, or non-owner source;
- a copy assignment signature without an lvalue owner receiver, const lvalue
  owner parameter, or lvalue owner result;
- an exact operation fact under an incomplete or different resolution context;
- a C++ alias or special-member payload applied to language `c`;
- a `complete` claim after an unresolved, conflicting, unsupported, cancelled,
  or budget-exhausted declaration; or
- a required identity or applicability use declared optional.

## Fixture digest

The compiler-argument and full resolution-context digests are recomputed from
`fixtures/profile-inputs/cpp-resolution.json`. The `cppsig-0.1` suffix in the
profile-local special-member fixture and all three canonical operation records
in `fixtures/profile-inputs/cpp-signatures.json` are likewise recomputed by
`scripts/validate-cpp-profile.py`. Altering a canonical input or only its
serialized digest fails deterministic validation.
