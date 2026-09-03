# CSMI repository guidance

Preserve CSMI as a small analyzer-neutral semantic interchange, not a union of
all source-language features or a universal compiler IR.

When adding or reviewing semantic vocabulary:

- Keep artifact identity, symbol identity, invocation boundaries, conservative
  transfer, provenance, and completeness as the stable core abstractions.
- Do not add a language-specific core field, enum value, type form, operation,
  or relationship merely because one language profile needs it.
- Prefer a sound mapping from a language construct to an existing, weaker
  portable fact. Such projection may reduce precision, but must not strengthen
  identity, applicability, semantic truth, coverage, or completeness.
- Keep resolver, compiler, ABI, packaging, and ecosystem evidence in an exact,
  versioned language or ecosystem profile.
- Keep reusable analysis domains such as value transfer, mutation, allocation,
  escape, invocation, ownership, and taint in independently versioned semantic
  profiles rather than growing the core.
- Extract a shared semantic profile only after materially different languages
  or ecosystems demonstrate the same analyzer-neutral meaning, comparison,
  conflict, merge, and completeness behavior.
- Preserve `unknown`, `partial`, unsupported, indeterminate, and
  uninterpretable outcomes when no sound portable mapping exists. Never repair
  missing semantics with names, source text, rendered signatures, regexes, or
  producer-local identifiers.
- Reuse established external standards for identity and metadata when their
  semantics fit; do not invent a CSMI-specific equivalent without need.

Every proposed core concept or standard profile should include independent
producer/consumer evidence, realistic positive cases and near misses, and an
explicit account of what information is retained, conservatively erased, or
left unsupported.
