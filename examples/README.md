# CSMI examples

The JSON files in this directory are non-normative component catalogs. They
keep several language and semantic cases together for design review, so their
outer grouping objects are not CSMI document roots.

`java-jvm-bifrost-mapping.json` is a non-normative reference adapter showing
which parsed class-file evidence can project a Bifrost-native record into the
standard JVM binary scheme. It also identifies producer-local IDs and display
text that are deliberately excluded from portable identity.

Complete representative documents using the normative field placement live in
`../fixtures/valid/` and validate against `../spec/0.1/schema.json`.
