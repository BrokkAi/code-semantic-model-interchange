---
title: Overview
description: What CSMI is, what it carries, and where its boundary sits.
---

> **Explanatory overview.** The normative semantic contract is the versioned
> specification and JSON Schema in the repository.

CSMI is an experimental interchange specification for portable semantic models
of code. It allows a producer to describe selected facts about a dependency or
API in a form an independently implemented analyzer can interpret.

The core covers artifact and symbol identity, declarations, procedure-summary
transfers, completeness, extensions, and content-addressed packs. It does not
standardize an analyzer's AST, control-flow graph, SSA, heap model, query
language, policy language, or finding format.

## Why an interchange boundary?

Analysis is strongest when every implementation is available, but real programs
depend on binaries, generated APIs, foreign-language libraries, runtimes, and
framework behavior. Analyzer-specific models fill that gap, but usually cannot
be reused by another analysis engine.

CSMI defines the portable portion of that knowledge while leaving richer
analyzer-owned concepts behind explicit, versioned extensions.
