#!/usr/bin/env node
// Independent wire consumer: no Python imports, Bifrost types, or runtime execution.
// The caller supplies accepted policy digests; documents cannot self-authorize.
import { createHash } from 'node:crypto';
import { readFileSync } from 'node:fs';
import { pathToFileURL } from 'node:url';

const VERSION = '0.2.0';
const SCHEMA = 'https://csmi.brokk.ai/schema/profiles/runtime-values/0.2/schema.json';
const CONTEXT = 'https://csmi.brokk.ai/runtime-context/';
const packages = new Map([
  ['pkg:generic/nodejs.org/node', 'semver'],
  ['pkg:generic/python.org/cpython', 'pypi'],
]);
const dimensions = ['platform', 'architecture', 'realm', 'moduleMode', 'launchMode', 'initializationBoundary'];

export function canonical(value) {
  if (Array.isArray(value)) {
    const members = [...new Set(value.map(canonical))];
    members.sort((a, b) => Buffer.compare(Buffer.from(a), Buffer.from(b)));
    return `[${members.join(',')}]`;
  }
  if (value !== null && typeof value === 'object') {
    return `{${Object.keys(value).sort().map(key => `${canonical(key)}:${canonical(value[key])}`).join(',')}}`;
  }
  if (typeof value === 'string') {
    for (let i = 0; i < value.length; i++) {
      const unit = value.charCodeAt(i);
      if (unit >= 0xd800 && unit <= 0xdbff) {
        const next = value.charCodeAt(++i);
        if (!(next >= 0xdc00 && next <= 0xdfff)) throw new Error('lone surrogate');
      } else if (unit >= 0xdc00 && unit <= 0xdfff) throw new Error('lone surrogate');
    }
  } else if (typeof value === 'number') {
    if (!Number.isSafeInteger(value)) throw new Error('profile requires exact integers');
  } else if (value !== null && typeof value !== 'boolean') throw new Error('non-JSON value');
  return JSON.stringify(value);
}

export const digest = value => createHash('sha256').update(canonical(value)).digest('hex');
const same = (a, b) => canonical(a) === canonical(b);
const conjunction = outcomes => ['not-matched', 'unsupported', 'indeterminate'].find(value => outcomes.includes(value)) ?? 'matched';

function interval(selector) {
  const [base, exact] = selector.purl.split('@');
  const scheme = packages.get(base);
  if (!scheme) return null;
  const stable = '(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)\\.(?:0|[1-9][0-9]*)';
  const number = text => text.split('.').map(BigInt);
  if (exact !== undefined) return new RegExp(`^${stable}$`).test(exact) ? [number(exact), true, number(exact), true] : null;
  if (!selector.versionRange?.startsWith(`vers:${scheme}/`)) return null;
  const text = selector.versionRange.split('/')[1];
  if (new RegExp(`^${stable}$`).test(text)) return [number(text), true, number(text), true];
  const bounds = text.match(new RegExp(`^(>=|>)(${stable})\\|(<|<=)(${stable})$`));
  return bounds ? [number(bounds[2]), bounds[1] === '>=', number(bounds[4]), bounds[3] === '<='] : null;
}

function compare(a, b) {
  for (let i = 0; i < 3; i++) if (a[i] !== b[i]) return a[i] < b[i] ? -1 : 1;
  return 0;
}

function covers(contract, target) {
  const [lo, li, hi, hii] = contract, [tlo, tli, thi, thii] = target;
  const before = compare(hi, tlo), after = compare(thi, lo);
  if (before < 0 || (before === 0 && !(hii && tli)) || after < 0 || (after === 0 && !(thii && li))) return 'not-matched';
  const lower = compare(lo, tlo), upper = compare(hi, thi);
  return (lower < 0 || (lower === 0 && (li || !tli))) && (upper > 0 || (upper === 0 && (hii || !thii))) ? 'matched' : 'indeterminate';
}

function artifactMatch(required = [], actual = []) {
  const groups = new Map();
  for (const entry of required) {
    const key = JSON.stringify([entry.coverage, entry.canonicalization]);
    groups.set(key, [...(groups.get(key) ?? []), entry]);
  }
  let missing = false;
  for (const alternatives of groups.values()) {
    let compared = false;
    for (const wanted of alternatives) for (const found of actual) {
      if (wanted.coverage !== found.coverage || wanted.canonicalization !== found.canonicalization || wanted.algorithm !== found.algorithm) continue;
      compared = true;
      if (wanted.value !== found.value) return 'not-matched';
    }
    missing ||= !compared;
  }
  return missing ? 'indeterminate' : 'matched';
}

export function selectorMatch(required, target) {
  if (!target) return 'indeterminate';
  const rb = required.purl.split('@')[0], tb = target.purl.split('@')[0];
  if (!packages.has(rb) || !packages.has(tb)) return 'unsupported';
  if (rb !== tb) return 'not-matched';
  const r = interval(required), t = interval(target);
  return conjunction([r && t ? covers(r, t) : 'unsupported', artifactMatch(required.digests, target.digests)]);
}

export function applicability(contract, target) {
  const definition = contract.definition, observed = target.definition;
  const alternatives = definition.applicability.selectors.map(selector => selectorMatch(selector, observed.runtime));
  const outcomes = [alternatives.includes('matched') ? 'matched' : alternatives.includes('unsupported') ? 'unsupported' : alternatives.includes('indeterminate') ? 'indeterminate' : 'not-matched'];
  const equality = definition.behavior.keyEquality;
  if (equality.version !== VERSION || !['exact-string', 'exact-index', 'platform-defined'].map(name => `https://csmi.brokk.ai/key-equality/${name}`).includes(equality.identifier)) outcomes.push('unsupported');
  const known = scheme => [CONTEXT + 'node', CONTEXT + 'cpython'].includes(scheme.identifier) && scheme.version === VERSION;
  if (!known(definition.context.scheme) || !known(observed.context.scheme)) outcomes.push('unsupported');
  else if (!same(definition.context.scheme, observed.context.scheme)) outcomes.push('not-matched');
  else {
    for (const field of dimensions) {
      if (observed.context[field] === 'unknown') outcomes.push('indeterminate');
      else if (!definition.context[field].includes(observed.context[field])) outcomes.push('not-matched');
    }
    if (definition.assumptions.some(value => !observed.assumptions.includes(value))) outcomes.push('indeterminate');
  }
  if (observed.basis === 'unknown' || observed.coverage.status !== 'complete') outcomes.push('indeterminate');
  return conjunction(outcomes);
}

export function activationInput(activation, contracts, targets) {
  return {
    targetDigest: targets.get(activation.targetId).targetDigest,
    surface: activation.surface,
    contracts: activation.candidateIds.map(id => contracts.get(id)),
    ...Object.fromEntries(['candidateCoverage', 'disabledIds', 'reviews', 'policy', 'outcome', 'selectedIds'].map(key => [key, activation[key]])),
  };
}

export function evaluate(activation, contracts, targets, acceptedPolicies = []) {
  const target = targets.get(activation.targetId);
  if (activation.candidateCoverage.status !== 'complete') return { outcome: 'indeterminate', selectedIds: [] };
  const candidates = activation.candidateIds.filter(id => !activation.disabledIds.includes(id)).map(id => contracts.get(id));
  if (!candidates.length) return { outcome: activation.candidateIds.length ? 'disabled' : 'not-matched', selectedIds: [] };
  const statuses = new Map(candidates.map(candidate => [candidate.contractId, applicability(candidate, target)]));
  const possible = candidates.filter(candidate => statuses.get(candidate.contractId) !== 'not-matched');
  const result = outcome => ({ outcome, selectedIds: [] });
  if (!possible.length) return result('not-matched');
  const identity = new Map();
  for (const candidate of possible) {
    const key = JSON.stringify([candidate.definition.identifier, candidate.definition.version]);
    const content = canonical(candidate.definition);
    if (identity.has(key) && identity.get(key) !== content) return result('conflict');
    identity.set(key, content);
  }
  const behavior = new Set(possible.map(candidate => canonical(Object.fromEntries(['surface', 'languages', 'assumptions', 'behavior'].map(key => [key, candidate.definition[key]])))));
  if (behavior.size > 1) return result('conflict');
  if ([...statuses.values()].includes('unsupported')) return result('unsupported');
  if ([...statuses.values()].includes('indeterminate')) return result('indeterminate');
  const policy = activation.policy;
  if (!acceptedPolicies.includes(digest(policy))) return result('review-required');
  for (const candidate of possible) {
    const reviews = activation.reviews.filter(review => review.contractDigest === candidate.contractDigest && review.targetDigest === target.targetDigest && review.purpose === policy.purpose && policy.trustedReviewers.includes(review.reviewer));
    if (!reviews.length || reviews.some(review => review.decision !== 'approved')) return result('review-required');
  }
  return { outcome: 'matched', selectedIds: possible.map(candidate => candidate.contractId).sort() };
}

export function consume(document, acceptedPolicies = []) {
  // Call after core/profile semantic validation; independently check negotiation
  // and digest joins relevant to applicability here.
  if (document.documentType !== 'semantic-document') throw new Error('invalid document');
  const results = [];
  for (const model of document.semanticModels) {
    const uses = (model.vocabularyUses ?? []).filter(use => use.identifier === 'csmi.runtime-values');
    const facts = (model.extensionFacts ?? []).filter(fact => fact.vocabulary === 'csmi.runtime-values');
    if (!uses.length && !facts.length) continue;
    if (uses.length !== 1 || uses[0].version !== VERSION || uses[0].schema !== SCHEMA || uses[0].requirement !== 'required') throw new Error('unsupported required vocabulary');
    if (facts.some(fact => fact.version !== VERSION)) throw new Error('unsupported fact version');
    const records = kind => {
      const entries = facts.filter(fact => fact.payload.kind === kind).map(fact => [fact.payload[`${kind.slice(8)}Id`], fact.payload]);
      const result = new Map(entries);
      if (result.size !== entries.length) throw new Error('duplicate local record identity');
      return result;
    };
    const contracts = records('runtime-contract'), targets = records('runtime-target');
    for (const candidate of contracts.values()) if (digest(candidate.definition) !== candidate.contractDigest) throw new Error('contract digest mismatch');
    for (const target of targets.values()) if (digest(target.definition) !== target.targetDigest) throw new Error('target digest mismatch');
    for (const fact of facts.filter(fact => fact.payload.kind === 'runtime-activation')) {
      const activation = fact.payload;
      const inventory = [...contracts.values()].filter(candidate => same(candidate.definition.surface, activation.surface)).map(candidate => candidate.contractId);
      if (!same(inventory, activation.candidateIds)) throw new Error('candidate inventory mismatch');
      const activationDigest = digest(activationInput(activation, contracts, targets));
      if (activationDigest !== activation.activationDigest) throw new Error('activation digest mismatch');
      results.push({ activationId: activation.activationId, ...evaluate(activation, contracts, targets, acceptedPolicies), activationDigest });
    }
  }
  return results;
}

if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  try {
    const input = JSON.parse(readFileSync(0, 'utf8'));
    const result = process.argv[2] === 'digest' ? digest(input) : consume(input.document, input.acceptedPolicies ?? []);
    process.stdout.write(JSON.stringify(result) + '\n');
  } catch (error) {
    process.stderr.write(error.message + '\n');
    process.exitCode = 1;
  }
}
