---
title: Python profile 0.1
description: Deterministic Python identity, artifact mapping, and compatibility for CSMI.
---

<span class="csmi-label csmi-label--normative">Normative profile</span>

`csmi.python` version `0.1.0` defines resolver-proven Python import and
declaration identity while keeping distribution coordinates, runtime symbols,
and declaration artifacts distinct.

The profile covers:

- PyPI distributions versus import packages and namespace contributors;
- interpreter and standard-library artifacts;
- runtime modules, inline `.pyi`, typeshed, and separate stub packages;
- aliases, re-exports, typing overloads, properties, generated declarations,
  and dynamic declarations;
- Python version, implementation, ABI, platform, extras, and project
  configuration compatibility; and
- required vocabulary behavior, fail-closed outcomes, and scoped completeness.

- [Read the normative profile source](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/python/0.1/profile.md)
- [Open the profile payload schema](/schema/profiles/python/0.1/schema.json)
- [Review the conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/python-profile.md)
- [Inspect the complete fixtures](https://github.com/BrokkAi/code-semantic-model-interchange/tree/main/fixtures/valid)
