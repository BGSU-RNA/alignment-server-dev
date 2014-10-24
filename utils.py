import logging
import collections as coll

from werkzeug.exceptions import BadRequest

import rnastructure.util.unit_ids as uid

RANGE_LIMIT = 50
PARTS_LIMIT = 5

PARSER = uid.UnitIdParser()

logger = logging.getLogger(__name__)


def split(raw):
    """Given a raw string of comma separated unit ids or unit id ranges this
    returns a list of tuples that represent that requested ranges. In the case
    where a range is only a single unit we return a tuple of the form (unit,
    unit), otherwise the tuple is (start, end). This is limited to only
    allowing up to 5 ranges or units to request.

    :raw: The raw input string to process.
    :returns: A list of tuples of the requested ranges.
    """
    parts = raw.split(',')
    if len(parts) == 0 or len(parts) > PARTS_LIMIT:
        raise BadRequest("Must give 1 to %s parts in a collection" %
                         PARTS_LIMIT)

    processed = []
    for part in parts:
        if not part:
            raise BadRequest("Cannot give empty part of a list")
        units = part.split(':')
        if len(units) == 1:
            if not units[0]:
                raise BadRequest("Cannot give empty unit")
            processed.append(tuple([units[0], units[0]]))
        elif len(units) == 2:
            if not units[0] or not units[1]:
                raise BadRequest("Both units in range must exist")
            processed.append(tuple(units))
        else:
            raise BadRequest("Range should must have 1 or 2 endpoints")

    return processed


def validate_pair(start, stop):
    """Process the start and stop endpoints into a tuple sutable for use by
    db.seqvar.
    """
    start_data = PARSER(start)
    stop_data = PARSER(stop)

    same = ['pdb', 'model', 'chain']
    for key in same:
        if start_data[key] != stop_data[key]:
            raise BadRequest("Pairs must have same %s" % key)
        if not start_data[key]:
            raise BadRequest("Pairs must have a non empty %s" % key)

    try:
        start_data['model'] = int(start_data['model'])
        stop_data['model'] = int(stop_data['model'])
    except:
        raise BadRequest("Invalid model number")

    if not start_data['number'] or not stop_data['number']:
        raise BadRequest("Endpoints must have a number")

    try:
        start_data['number'] = int(start_data['number'])
        stop_data['number'] = int(stop_data['number'])
    except:
        raise BadRequest("Invalid endpoint number")

    return (start_data, stop_data)


def ranges(data):
    if 'units' not in data:
        raise BadRequest("Must specify units to use")

    pdb = None
    model = None
    ranges = []

    for (start, stop) in split(data['units']):
        data = validate_pair(start, stop)
        if pdb is None:
            pdb = data[0]['pdb']
            model = data[0]['model']

        if data[0]['pdb'] != pdb:
            raise BadRequest("All parts of a collection must have same pdb")

        if data[0]['model'] != model:
            raise BadRequest("All parts of a collection must have same model")

        ranges.append(data)

    return pdb, model, ranges


def validate(pdb, model, ranges, known):
    mapping = coll.defaultdict(lambda: coll.defaultdict(set))
    for entry in known:
        mapping[entry['pdb']][entry['model_number']].add(entry['chain_id'])

    if pdb not in mapping:
        raise BadRequest("Unmapped PDB %s" % pdb)

    if model not in mapping[pdb]:
        raise BadRequest("Unmapped model %s for %s" % (model, pdb))

    for (start, stop) in ranges:
        valid = mapping[pdb][model]
        if start['chain'] not in valid:
            raise BadRequest("Unmapped chain %s for pdb %s, model %s" %
                             (start['chain'], pdb, model))
        if stop['chain'] not in valid:
            raise BadRequest("Unmapped chain %s for pdb %s, model %s" %
                             (stop['chain'], pdb, model))
        if stop['number'] < start['number']:
            raise BadRequest("Must request ranges 5' to 3'")
    return True


def translate(translator, ranges):
    mappings = coll.defaultdict(dict)

    def number(data):
        key = (data['number'], data.get('insertion_code', None))
        return mappings[data['chain']].get(key, data['number'])

    translated = []
    for (start, stop) in ranges:
        chain = start['chain']
        if chain not in mappings:
            mappings[chain] = translator(chain)

        start['number'] = number(start)
        stop['number'] = number(stop)

        if stop['number'] - start['number'] > RANGE_LIMIT:
            raise BadRequest("Ranges must be less than %s large", RANGE_LIMIT)

        translated.append((start, stop))
    return translated
