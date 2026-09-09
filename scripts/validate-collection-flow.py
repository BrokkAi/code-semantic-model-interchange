#!/usr/bin/env python3
"""Collection-flow reference validation and independent token-set consumer."""
import copy
import json
from pathlib import Path
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / 'profiles/collection-flow/0.1'
IDENTIFIER = 'csmi.collection-flow'
VERSION = '0.1.0'
SCHEMA = json.loads((PROFILE / 'schema.json').read_text())
VALIDATOR = Draft202012Validator(SCHEMA)
CORE = Draft202012Validator(json.loads((ROOT / 'spec/0.1/schema.json').read_text()))


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'))


def shape_at(location, roots):
    shape = roots.get(canonical(location['root']))
    if shape is None:
        raise ValueError('missing root shape')
    for step in location.get('projection', {}).get('steps', []):
        kind = step['kind']
        if kind == 'entry':
            if shape['kind'] != 'keyed':
                raise ValueError('entry requires keyed shape')
            shape = {'kind': 'entry', **{k: v for k, v in shape.items() if k != 'kind'}}
        elif kind in ('entry-key', 'entry-value'):
            if shape['kind'] != 'entry':
                raise ValueError('entry member requires entry')
            shape = shape['key' if kind == 'entry-key' else 'value']
        elif kind == 'component':
            position = step['args']['position']
            if shape['kind'] == 'entry':
                if 'entryComponents' not in shape:
                    raise ValueError('entry has no product evidence')
                components = [shape[k] for k in shape['entryComponents']]
            elif shape['kind'] == 'product':
                components = shape['components']
            else:
                raise ValueError('component requires product')
            if position >= len(components):
                raise ValueError('component out of range')
            shape = components[position]
    return shape


def uncertain(value):
    if isinstance(value, dict):
        return value.get('kind') in ('unknown', 'unsupported') or any(uncertain(v) for v in value.values())
    return isinstance(value, list) and any(uncertain(v) for v in value)


def payload_errors(payload, declarations):
    errors = [e.message for e in VALIDATOR.iter_errors(payload)]
    if errors:
        return errors
    decl = declarations.get(payload['callable'], {})
    callable_shape = decl.get('callable')
    if decl.get('category') != 'callable' or not callable_shape:
        return ['callable requires local callable shape']
    for field in ('parameters', 'results'):
        if [p['position'] for p in callable_shape[field]] != list(range(len(callable_shape[field]))):
            errors.append('callable positions must be contiguous and ordered')
    roots = {}
    def root_check(root):
        role = root['role']
        if role == 'receiver' and 'receiver' not in callable_shape:
            errors.append('receiver absent from callable')
        if role in ('parameter', 'result'):
            sequence = callable_shape['parameters' if role == 'parameter' else 'results']
            if root['position'] not in [p['position'] for p in sequence]:
                errors.append('boundary position out of range')
        if role == 'capture' and declarations.get(root['symbol'], {}).get('category') != 'value':
            errors.append('capture requires value declaration')
    for entry in payload['roots']:
        root_check(entry['root'])
        key = canonical(entry['root'])
        if key in roots:
            errors.append('duplicate root shape')
        roots[key] = entry['shape']
    substitution = payload.get('receiverSubstitution', {})
    if substitution.get('kind') == 'receiver-arguments':
        owner = declarations.get(substitution['declaration'], {})
        parameters = owner.get('genericParameters', [])
        receiver_type = callable_shape.get('receiver', {}).get('type', {})
        if owner.get('category') != 'type' or not parameters:
            errors.append('substitution requires generic type declaration')
        if receiver_type.get('kind') != 'reference' or receiver_type.get('symbol') != substitution['declaration']:
            errors.append('receiver must name exact substitution declaration')
        if receiver_type.get('arguments') != [{'kind': 'parameter', 'symbol': p['symbol']} for p in parameters]:
            errors.append('receiver arguments must preserve declared parameter order')
        if len(receiver_type.get('arguments', [])) != len(parameters):
            errors.append('receiver generic arity mismatch')
        if [p['position'] for p in parameters] != list(range(len(parameters))):
            errors.append('generic positions must be contiguous')
        for p in parameters:
            if p['kind'] != 'type' or declarations.get(p['symbol'], {}).get('owner') != substitution['declaration'] or declarations.get(p['symbol'], {}).get('category') != 'type-parameter':
                errors.append('generic parameter kind or ownership mismatch')
    def location_check(location):
        root_check(location['root'])
        try:
            result = shape_at(location, roots)
        except ValueError as error:
            errors.append(str(error))
            return None
        for step in location.get('projection', {}).get('steps', []):
            if step['kind'] == 'entry':
                key = step['args']['key']
                if key['kind'] == 'parameter' and key['position'] not in [p['position'] for p in callable_shape['parameters']]:
                    errors.append('key parameter out of range')
        return result
    for transfer in payload['transfers']:
        location_check(transfer['source'])
        location_check(transfer['destination'])
        if transfer['destination']['root']['role'] == 'parameter' and 'projection' not in transfer['destination']:
            errors.append('unprojected parameter writeback unsupported')
    def layout(shape):
        if shape is None:
            return None
        if shape['kind'] == 'entry' and 'entryComponents' in shape:
            return {'kind': 'product', 'components': [layout(shape[k]) for k in shape['entryComponents']]}
        if shape['kind'] == 'product':
            return {'kind': 'product', 'components': [layout(c) for c in shape['components']]}
        return shape
    for invocation in payload['invocations']:
        location_check(invocation['callback'])
        for argument in invocation['arguments']:
            source_shape = location_check(argument['source'])
            if argument['parameter'] >= len(invocation['parameters']):
                errors.append('callback parameter out of range')
            elif source_shape is not None and not uncertain(source_shape) and not uncertain(invocation['parameters'][argument['parameter']]) and layout(source_shape) != layout(invocation['parameters'][argument['parameter']]):
                errors.append('callback argument structural layout mismatch')
    def type_check(value):
        if isinstance(value, dict):
            if value.get('kind') == 'parameter':
                symbol = value.get('symbol')
                if isinstance(symbol, str) and declarations.get(symbol, {}).get('category') != 'type-parameter':
                    errors.append('unresolved type parameter')
            if value.get('kind') == 'reference':
                local = value.get('symbol')
                if local and declarations.get(local, {}).get('category') not in ('type', 'type-alias'):
                    errors.append('unresolved type reference')
            for child in value.values():
                type_check(child)
        elif isinstance(value, list):
            for child in value:
                type_check(child)
    type_check(payload)
    return errors


def contract_key(value):
    if isinstance(value, dict):
        result = {k: contract_key(v) for k, v in value.items()}
        set_fields = {'roots', 'transfers', 'invocations'}
        if 'callback' in value:
            set_fields.add('arguments')
        for field in set_fields & result.keys():
            result[field] = sorted({canonical(x) for x in result[field]})
        return result
    if isinstance(value, list):
        return [contract_key(x) for x in value]
    return value


def document_errors(document):
    errors = [e.message for e in CORE.iter_errors(document)]
    if errors:
        return errors
    provenance = {p['id'] for p in document.get('provenanceRecords', [])}
    for model in document['semanticModels']:
        symbols = {symbol['id'] for symbol in model.get('symbols', [])}
        declarations = {d['symbol']: d for d in model.get('declarations', [])}
        if not set(declarations) <= symbols:
            errors.append('declaration missing structured symbol identity')
        if len(declarations) != len(model.get('declarations', [])):
            errors.append('duplicate declaration identity')
        uses = [u for u in model.get('vocabularyUses', []) if u['identifier'] == IDENTIFIER]
        if len(uses) != 1 or uses[0]['version'] != VERSION or uses[0]['schema'] != SCHEMA['$id'] or uses[0]['requirement'] != 'required':
            errors.append('exact required vocabulary use missing')
            continue
        complete_aspects = {(x['scope'].get('symbol'), x['scope'].get('aspect')) for x in model.get('completenessStatements', []) if x['family'] == 'declaration-aspects' and x['status'] == 'complete'}
        affected = {(a.get('family'), canonical(a.get('scope'))) for a in uses[0]['affects'] if a['kind'] == 'fact-family'}
        facts = {}
        for fact in model.get('extensionFacts', []):
            if fact['vocabulary'] != IDENTIFIER:
                continue
            inherited = [document['defaultProvenance']] if 'defaultProvenance' in document else []
            evidence = fact.get('provenance', inherited)
            if not evidence or any(p not in provenance for p in evidence):
                errors.append('unresolved fact provenance')
            payload = fact['payload']
            structural = list(VALIDATOR.iter_errors(payload))
            if structural:
                errors.append('invalid collection-flow payload: ' + structural[0].message)
                continue
            scope = {'callable': payload.get('callable')}
            key = ('collection-flows', canonical(scope))
            if fact['version'] != VERSION or fact['family'] != key[0] or fact['scope'] != scope:
                errors.append('fact version family or scope mismatch')
            if key not in affected:
                errors.append('fact absent from exact affects')
            if (payload.get('callable'), 'callable-shape') not in complete_aspects:
                errors.append('missing complete callable-shape evidence')
            substitution = payload.get('receiverSubstitution', {})
            if substitution.get('kind') == 'receiver-arguments' and (substitution['declaration'], 'generic-parameters') not in complete_aspects:
                errors.append('missing complete generic-parameters evidence')
            errors.extend(payload_errors(payload, declarations))
            facts.setdefault(key, []).append(payload)
        seen = set()
        for statement in model.get('completenessStatements', []):
            if statement.get('vocabulary') != IDENTIFIER:
                continue
            key = (statement['family'], canonical(statement['scope']))
            if statement.get('version') != VERSION or key not in affected or key[0] != 'collection-flows' or set(statement['scope']) != {'callable'} or statement['scope']['callable'] not in declarations:
                errors.append('invalid completeness scope or version')
            if key in seen:
                errors.append('duplicate completeness scope')
            seen.add(key)
            if statement['status'] == 'complete' and (any(uncertain(p) for p in facts.get(key, [])) or len({canonical(contract_key(p)) for p in facts.get(key, [])}) > 1):
                errors.append('complete scope contains uncertainty or conflict')
    return errors


def substitute(expression, bindings):
    """Recursive structural substitution; unknown never becomes an exact type."""
    if expression['kind'] == 'parameter':
        return copy.deepcopy(bindings.get(expression['symbol'], {'kind': 'unknown'}))
    result = copy.deepcopy(expression)
    if result['kind'] == 'reference' and 'arguments' in result:
        result['arguments'] = [substitute(x, bindings) for x in result['arguments']]
    return result


def receiver_bindings(payload, declarations, actual):
    """After exact identity resolution into this model, instantiate the recipe."""
    recipe = payload.get('receiverSubstitution', {})
    if recipe.get('kind') != 'receiver-arguments':
        return {'status': 'unsupported', 'limitation': {'kind': 'unsupported-construct'}}
    declaration = recipe['declaration']
    parameters = declarations[declaration]['genericParameters']
    if actual.get('kind') != 'reference' or actual.get('symbol') != declaration:
        return {'status': 'indeterminate', 'limitation': {'kind': 'unresolved-identity'}}
    arguments = actual.get('arguments', [])
    if len(arguments) != len(parameters) or uncertain(arguments):
        return {'status': 'partial', 'limitation': {'kind': 'unresolved-type'}}
    return {'status': 'matched', 'bindings': {p['symbol']: copy.deepcopy(a) for p, a in zip(parameters, arguments)}}


def main():
    Draft202012Validator.check_schema(SCHEMA)
    core_defs = CORE.schema['$defs']
    for name in ('typeExpression', 'referenceType', 'parameterType', 'intrinsicType', 'unknownType', 'inputBoundaryRoot', 'outputBoundaryRoot'):
        assert SCHEMA['$defs'][name] == core_defs[name], name
    counts = {}
    for group in ('valid', 'invalid'):
        paths = sorted((PROFILE / 'fixtures' / group).glob('*.json'))
        assert paths, group
        for path in paths:
            errors = list(VALIDATOR.iter_errors(json.loads(path.read_text())))
            assert bool(errors) == (group == 'invalid'), (path, errors)
        counts[group] = len(paths)
    documents = sorted((PROFILE / 'fixtures/documents').glob('*.json'))
    assert documents
    for path in documents:
        doc = json.loads(path.read_text())
        assert not document_errors(doc), (path, document_errors(doc))
    semantic_paths = list((PROFILE / 'fixtures/semantic-invalid').glob('*.json'))
    assert semantic_paths
    for path in semantic_paths:
        doc = json.loads(path.read_text())
        assert not list(CORE.iter_errors(doc)), path
        assert document_errors(doc), path
    doc = json.loads((PROFILE / 'fixtures/documents/entry-product.json').read_text())
    model = doc['semanticModels'][0]
    declarations = {d['symbol']: d for d in model['declarations']}
    payload = model['extensionFacts'][0]['payload']
    actual = {'kind': 'reference', 'symbol': 'Map', 'arguments': [{'kind': 'reference', 'symbol': 'Key'}, {'kind': 'reference', 'symbol': 'Nested', 'arguments': [{'kind': 'reference', 'symbol': 'Payload'}]}]}
    binding = receiver_bindings(payload, declarations, actual)
    assert binding['status'] == 'matched'
    assert substitute({'kind': 'parameter', 'symbol': 'V'}, binding['bindings']) == actual['arguments'][1]
    assert receiver_bindings(payload, declarations, dict(actual, symbol='UnrelatedMap'))['status'] == 'indeterminate'
    assert receiver_bindings(payload, declarations, {'kind': 'reference', 'symbol': 'Map'})['status'] == 'partial'
    assert receiver_bindings(payload, declarations, dict(actual, arguments=[{'kind': 'unknown'}, {'kind': 'unknown'}]))['status'] == 'partial'
    # Independent consumer interprets paths into token sets, not producer IDs.
    def select(location, receiver, arguments):
        root = location['root']
        initial = receiver if root['role'] == 'receiver' else arguments[root['position']]
        values = [initial]
        steps = location.get('projection', {}).get('steps', [])
        for step in steps:
            if step['kind'] == 'entry':
                key = step['args']['key']
                values = [pair for value in values for pair in (
                    list(value.items()) if key['kind'] == 'all' else
                    [(arguments[key['position']], value[arguments[key['position']]])]
                )]
            elif step['kind'] in ('entry-key', 'entry-value'):
                values = [pair[0 if step['kind'] == 'entry-key' else 1] for pair in values]
            elif step['kind'] == 'component':
                values = [pair[step['args']['position']] for pair in values]
        return values if steps else initial
    # Consume independently authored wire fixtures, preserving callback arity.
    for filename, expected in [('entry-callback.json', [[('key-token', 'value-token')]]), ('two-argument-callback.json', [['key-token'], ['value-token']])]:
        payload = json.loads((PROFILE / 'fixtures/valid' / filename).read_text())
        invocation = payload['invocations'][0]
        bound = [[] for _ in invocation['parameters']]
        for argument in invocation['arguments']:
            bound[argument['parameter']].extend(select(argument['source'], {'key-token': 'value-token'}, ['callback-token']))
        assert bound == expected
    component = json.loads((PROFILE / 'fixtures/valid/product-component.json').read_text())
    local_binding = select(component['transfers'][0]['source'], {}, [('key-token', 'value-token')])
    assert local_binding == ['value-token']
    update = json.loads((PROFILE / 'fixtures/valid/update.json').read_text())
    transfer = update['transfers'][0]
    arguments = ['selected-key', 'new-token']
    assert select(transfer['source'], {}, arguments) == 'new-token'
    assert select(transfer['destination'], {'selected-key': 'old-token', 'other-key': 'other-token'}, arguments) == ['old-token']
    entry = {'root': {'phase': 'input', 'role': 'receiver'}, 'projection': {'scheme': IDENTIFIER, 'schemeVersion': VERSION, 'steps': [{'kind': 'entry', 'args': {'key': {'kind': 'all'}}}]}}
    assert select(entry, {'key-token': 'value-token'}, []) == [('key-token', 'value-token')]
    assert select(entry, {}, []) == []
    value = copy.deepcopy(entry)
    value['projection']['steps'].append({'kind': 'component', 'args': {'position': 1}})
    assert select(value, {'key-token': 'value-token'}, []) == ['value-token']
    nested = {'kind': 'reference', 'symbol': 'Container', 'arguments': [{'kind': 'parameter', 'symbol': 'V'}]}
    assert substitute(nested, {'V': {'kind': 'reference', 'symbol': 'Payload'}})['arguments'][0]['symbol'] == 'Payload'
    assert substitute({'kind': 'parameter', 'symbol': 'missing'}, {}) == {'kind': 'unknown'}
    print(f'Collection-flow: {counts}, {len(documents)} documents, {len(semantic_paths)} semantic rejects and independent projection/substitution passed')


if __name__ == '__main__':
    main()
