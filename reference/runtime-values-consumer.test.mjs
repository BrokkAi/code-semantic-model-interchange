#!/usr/bin/env node

import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';

import {
  applicability,
  canonical,
  consume,
  digest,
  evaluate,
  selectorMatch,
} from './runtime-values-consumer.mjs';

const FIXTURE_PATH = new URL(
  '../profiles/runtime-values/0.2/fixtures/documents/valid/portable-node-env.json',
  import.meta.url,
);

function loadFixture() {
  return JSON.parse(readFileSync(FIXTURE_PATH, 'utf8'));
}

function payload(document, kind) {
  const facts = document.semanticModels[0].extensionFacts;
  return facts.find(fact => fact.payload.kind === kind).payload;
}

function clone(value) {
  return structuredClone(value);
}

function acceptedPolicyDigest(document) {
  return digest(payload(document, 'runtime-activation').policy);
}

function testActivation(document, { candidateIds, disabledIds = [], coverage = 'complete' }) {
  const activation = clone(payload(document, 'runtime-activation'));
  const contracts = new Map(document.semanticModels[0].extensionFacts
    .filter(fact => fact.payload.kind === 'runtime-contract')
    .map(fact => [fact.payload.contractId, fact.payload]));
  const targets = new Map(document.semanticModels[0].extensionFacts
    .filter(fact => fact.payload.kind === 'runtime-target')
    .map(fact => [fact.payload.targetId, fact.payload]));
  activation.candidateIds = candidateIds;
  activation.disabledIds = disabledIds;
  activation.candidateCoverage = { status: coverage };
  return evaluate(activation, contracts, targets, [digest(activation.policy)]);
}

test('canonicalizes object keys, Unicode strings, and set-valued arrays deterministically', () => {
  const value = { z: '😀', a: ['z', 'a', 'é', 'a'] };
  assert.equal(canonical(value), '{"a":["a","z","é"],"z":"😀"}');
  assert.equal(digest(value), digest({ a: ['a', 'z', 'é'], z: '😀' }));
  assert.throws(() => canonical('lone \ud800 surrogate'), /lone surrogate/);
});

test('portable fixture accepts only externally trusted policy and preserves its digest', () => {
  const document = loadFixture();
  assert.deepEqual(consume(document, []), [{
    activationId: 'portable-node-env-activation',
    outcome: 'review-required',
    selectedIds: [],
    activationDigest: payload(document, 'runtime-activation').activationDigest,
  }]);
  assert.deepEqual(consume(document, [acceptedPolicyDigest(document)]), [{
    activationId: 'portable-node-env-activation',
    outcome: 'matched',
    selectedIds: ['node-env-portable'],
    activationDigest: payload(document, 'runtime-activation').activationDigest,
  }]);
});

test('version ranges require complete target coverage and refuse prereleases', () => {
  const required = { purl: 'pkg:generic/nodejs.org/node', versionRange: 'vers:semver/>=22.11.0|<23.0.0' };
  const full = { purl: 'pkg:generic/nodejs.org/node@22.11.0' };
  const partial = { purl: 'pkg:generic/nodejs.org/node', versionRange: 'vers:semver/>=22.0.0|<24.0.0' };
  const disjoint = { purl: 'pkg:generic/nodejs.org/node', versionRange: 'vers:semver/>=23.0.0|<24.0.0' };
  const prerelease = { purl: 'pkg:generic/nodejs.org/node', versionRange: 'vers:semver/>=23.0.0-pre.1|<23.1.0' };
  assert.equal(selectorMatch(required, full), 'matched');
  assert.equal(selectorMatch(required, partial), 'indeterminate');
  assert.equal(selectorMatch(required, disjoint), 'not-matched');
  assert.equal(selectorMatch(required, prerelease), 'unsupported');
});

test('artifact bytes are compared only within an identical coverage and canonicalization role', () => {
  const digestValue = '1'.repeat(64);
  const required = {
    purl: 'pkg:generic/nodejs.org/node@22.11.0',
    digests: [{
      algorithm: 'sha-256',
      coverage: 'official-distribution-archive',
      canonicalization: 'https://csmi.brokk.ai/artifact-canonicalization/archive',
      value: digestValue,
    }],
  };
  const found = value => ({
    purl: 'pkg:generic/nodejs.org/node@22.11.0',
    digests: [{
      algorithm: 'sha-256',
      coverage: 'official-distribution-archive',
      canonicalization: 'https://csmi.brokk.ai/artifact-canonicalization/archive',
      value,
    }],
  });
  assert.equal(selectorMatch(required, found(digestValue)), 'matched');
  assert.equal(selectorMatch(required, found('2'.repeat(64))), 'not-matched');
  const otherCoverage = found(digestValue);
  otherCoverage.digests[0].coverage = 'contract-content';
  assert.equal(selectorMatch(required, otherCoverage), 'indeterminate');
  const otherCanonicalization = found(digestValue);
  otherCanonicalization.digests[0].canonicalization += '-other';
  assert.equal(selectorMatch(required, otherCanonicalization), 'indeterminate');
  assert.equal(selectorMatch(required, { purl: 'pkg:generic/nodejs.org/node@22.11.0' }), 'indeterminate');
});

test('candidate identity or behavior conflict wins over trust and selection', () => {
  const document = loadFixture();
  const contract = payload(document, 'runtime-contract');
  const conflicting = clone(contract);
  conflicting.contractId = 'node-env-conflicting';
  conflicting.definition.behavior.absent = 'exception';
  conflicting.contractDigest = digest(conflicting.definition);
  const target = payload(document, 'runtime-target');
  const activation = clone(payload(document, 'runtime-activation'));
  activation.candidateIds = ['node-env-portable', 'node-env-conflicting'];
  activation.disabledIds = [];
  assert.deepEqual(
    evaluate(activation, new Map([
      ['node-env-portable', contract],
      ['node-env-conflicting', conflicting],
    ]), new Map([['portable-node-env-target', target]]), [digest(activation.policy)]),
    { outcome: 'conflict', selectedIds: [] },
  );
});

test('partial inventory with zero known candidates remains indeterminate', () => {
  const document = loadFixture();
  assert.deepEqual(
    testActivation(document, { candidateIds: [], coverage: 'partial' }),
    { outcome: 'indeterminate', selectedIds: [] },
  );
});

test('partial inventory with all known candidates disabled remains indeterminate', () => {
  const document = loadFixture();
  assert.deepEqual(
    testActivation(document, {
      candidateIds: ['node-env-portable'],
      disabledIds: ['node-env-portable'],
      coverage: 'partial',
    }),
    { outcome: 'indeterminate', selectedIds: [] },
  );
});

test('a wholly contained target range is eligible under the portable contract', () => {
  const document = loadFixture();
  const contract = payload(document, 'runtime-contract');
  const target = payload(document, 'runtime-target');
  const originalRuntime = target.definition.runtime;
  target.definition.runtime = { purl: 'pkg:generic/nodejs.org/node@22.12.0' };
  assert.equal(applicability(contract, target), 'matched');
  target.definition.runtime = originalRuntime;
});

test('a partially overlapping target range stays conditional', () => {
  const document = loadFixture();
  const contract = payload(document, 'runtime-contract');
  const target = payload(document, 'runtime-target');
  const originalRuntime = target.definition.runtime;
  target.definition.runtime = {
    purl: 'pkg:generic/nodejs.org/node',
    versionRange: 'vers:semver/>=22.0.0|<24.0.0',
  };
  assert.equal(applicability(contract, target), 'indeterminate');
  target.definition.runtime = originalRuntime;
});

test('wire consumption rejects an altered contract still carrying its old digest', () => {
  const document = loadFixture();
  const contractFact = document.semanticModels[0].extensionFacts
    .find(fact => fact.payload.kind === 'runtime-contract');
  contractFact.payload.definition.behavior.absent = 'exception';
  assert.throws(() => consume(document, [acceptedPolicyDigest(document)]), /contract digest mismatch/);
});

test('wire consumption refuses a relabeled or unknown required profile version', () => {
  for (const version of ['0.1.0', '0.3.0']) {
    const document = loadFixture();
    document.semanticModels[0].vocabularyUses[0].version = version;
    assert.throws(() => consume(document), /unsupported required vocabulary/);
  }
});

test('duplicate local contract handles cannot overwrite the inventory', () => {
  const document = loadFixture();
  const duplicate = clone(document.semanticModels[0].extensionFacts.find(fact => fact.payload.kind === 'runtime-contract'));
  document.semanticModels[0].extensionFacts.push(duplicate);
  assert.throws(() => consume(document), /duplicate local record identity/);
});

test('unaffected core models do not require runtime vocabulary support', () => {
  const document = loadFixture();
  const unaffected = JSON.parse(readFileSync(new URL('../fixtures/valid/partial-summary.json', import.meta.url), 'utf8')).semanticModels[0];
  const expected = consume(document);
  document.semanticModels.push(unaffected);
  assert.deepEqual(consume(document), expected);
});
