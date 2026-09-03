# Contributing

Code Semantic Model Interchange (CSMI) is currently in an early specification phase.

Design feedback, use cases, counterexamples, interoperability concerns, and references to related work are welcome through GitHub Issues.

## Pull requests

External pull requests are **not accepted at this stage**.

Changes to the specification repository will be authored or incorporated by BrokkAi maintainers while the core model, licensing posture, and governance process are still being established.

This policy is intended to keep specification authorship and licensing straightforward during the experimental phase. It may change later if the project adopts a formal contribution agreement, developer certificate of origin, standards-process policy, or other governance mechanism.

## Issues

Issues are welcome for topics such as:

- semantic concepts that should or should not be part of the portable core;
- interoperability requirements from other analyzers;
- mappings to existing formats such as CodeQL models, SCIP, SARIF, or Code Property Graph tooling;
- examples where the proposed model cannot represent an important dependency behavior;
- completeness and soundness concerns;
- package, artifact, or symbol identity;
- extension and versioning design; and
- corrections to the specification or related-work discussion.

Please focus issues on the interchange problem rather than on Bifrost-specific implementation details unless those details expose a broader specification requirement.

## Proposing semantic vocabulary

CSMI is a portable semantic algebra, not a union of every source language's
features. A proposal for a core concept, standard profile, or extension should
therefore answer:

1. What analyzer-neutral observation is being exchanged?
2. Can two independent consumers implement its meaning without embedding one
   language's compiler or one producer's internal model?
3. What are its equality, conflict, merge, and completeness rules?
4. What exact semantic units does it affect, when is its use required, and what
   remains independently interpretable when it is unsupported?
5. Which materially different languages or ecosystems can map to it without
   treating one of them as the canonical shape?
6. What information does the mapping retain, conservatively erase, leave
   unknown, or report as unsupported?
7. Can existing core facts express a sound weaker approximation instead?
8. Which resolver, compiler, ABI, packaging, or ecosystem evidence must remain
   in a language-specific profile?

A lossy projection is useful when it remains sound: it may weaken precision but
must not strengthen identity, applicability, semantic truth, coverage, or
completeness. An unresolved declaration must not become an approximate named
symbol, and partial coverage must not become a complete portable summary.

New core concepts require evidence of broad interoperability. A concept used by
only one language should normally begin in that language's exact-versioned
profile. When several profiles independently demonstrate equivalent semantics,
the common observation may be extracted into a shared semantic profile without
moving language-specific evidence into the core.

Proposals should include realistic positive examples and near misses for each
claimed mapping. Executable producer and independent-consumer evidence is
preferred over schema shape alone.

## Code of conduct

BrokkAi maintainers may close discussions that are abusive, off-topic, or otherwise prevent productive technical discussion.
