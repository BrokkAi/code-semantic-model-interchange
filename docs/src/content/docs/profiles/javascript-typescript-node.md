---
title: JavaScript, TypeScript, and Node profiles
description: Versioned runtime identity, declaration identity, and compatibility profiles for JavaScript, TypeScript, and Node.
---

<span class="csmi-label csmi-label--normative">Normative profile family · v0.1</span>

The JavaScript, TypeScript, and Node profile family defines two exact standard
vocabularies without opening the language-neutral CSMI core:

- `csmi.javascript-typescript` `0.1.0` defines resolver-proven JavaScript runtime
  identity, TypeScript declaration identity, CommonJS/ESM binding evidence, and
  explicit runtime-to-declaration mappings.
- `csmi.node-compatibility` `0.1.0` defines Node runtime, module-resolution,
  package-condition, TypeScript-resolution, and project-configuration
  compatibility values.

The profile keeps runtime and declaration artifacts distinct. For example, the
Node distribution and `@types/node` have separate PURLs, symbols, provenance,
and completeness scopes even when an explicit fact relates their bindings.
Likewise, bare `child_process` and `node:child_process` resolve to one builtin
identity only when the selected exact Node distribution proves that alias.

- [Read the normative profile definition on GitHub](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/profiles/javascript-typescript-node/0.1/profile.md)
- [Open the JavaScript/TypeScript payload schema](/schema/profiles/javascript-typescript/0.1/schema.json)
- [Open the Node compatibility schema](/schema/profiles/node-compatibility/0.1/schema.json)
- [Review the conformance cases](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/conformance/javascript-typescript-node.md)
- [Inspect the representative valid fixture](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/fixtures/valid/javascript-typescript-node.json)
- [Read the Bifrost native-model reference mapping](https://github.com/BrokkAi/code-semantic-model-interchange/blob/main/reference/bifrost-javascript-typescript-node.md)
- [Run the independent Node builtin consumer demo](https://github.com/BrokkAi/csmi-demo/tree/main/scenarios/node-builtin-alias)

Unsupported required identity or compatibility semantics fail closed. A
consumer must not recover from missing support or evidence by comparing display
names, raw module strings, source text, filenames, or analyzer-local IDs.
