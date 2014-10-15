import logging
import collections as coll

from werkzeug.exceptions import BadRequest

import rnastructure.util.unit_ids as uid

RANGE_LIMIT = 50

PARSER = uid.UnitIdParser()

logger = logging.getLogger(__name__)


def parse_units(raw):
    """Given a raw string of comma separated unit ids or unit id ranges this
    returns a list of tuples that represent that requested ranges. In the case
    where a range is only a single unit we return a tuple of the form (unit,
    unit), otherwise the tuple is (start, end). This is limited to only
    allowing up to 5 ranges or units to request.

    :raw: The raw input string to process.
    :returns: A list of tuples of the requested ranges.
    """
    parts = raw.split(',')
    if len(parts) == 0 or len(parts) > 5:
        raise BadRequest("Must give 1 to 5 parts in a collection")

    processed = []
    for part in parts:
        units = part.split(':')
        if len(units) == 1:
            processed.append(tuple([units[0], units[0]]))
        elif len(units) == 2:
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
        model = int(start_data['model'])
    except:
        raise BadRequest("Invalid model number")

    if not start_data['number'] or not stop_data['number']:
        raise BadRequest("Endpoints must have a number")

    try:
        start_num = int(start_data['number'])
        stop_num = int(stop_data['number'])
    except:
        raise BadRequest("Invalid endpoint number")

    return (start_data['pdb'], model,
            (start_data['chain'], start_num, stop_num))


def ranges(data):
    if 'units' not in data:
        raise BadRequest("Must specify units to use")
    raw_units = data['units']
    units = parse_units(raw_units)
    pdb = None
    model = None
    ranges = []

    for (start, stop) in units:
        data = validate_pair(start, stop)
        if pdb is None:
            pdb = data[0]
            model = data[1]

        if data[0] != pdb:
            raise BadRequest("All parts of a collection must have same pdb")

        if data[1] != model:
            raise BadRequest("All parts of a collection must have same model")

        ranges.append(data[2])

    return pdb, model, ranges


def validate_ranges(pdb, model, ranges, known):
    mapping = coll.defaultdict(lambda: coll.defaultdict(set))
    for entry in known:
        mapping[entry['pdb']][entry['model_number']].add(entry['chain_id'])

    if pdb not in mapping:
        raise BadRequest("Unmapped PDB %s" % pdb)

    if model not in mapping[pdb]:
        raise BadRequest("Unmapped model %s for %s" % (model, pdb))

    for (chain, _, _) in ranges:
        if chain not in mapping[pdb][model]:
            raise BadRequest("Unmapped chain %s for pdb %s, model %s" %
                             (chain, pdb, model))
    return True
