import logging

from flask import abort

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
        abort(400)

    processed = []
    for part in parts:
        units = part.split(':')
        if len(units) == 1:
            processed.append(tuple([units[0], units[0]]))
        elif len(units) == 2:
            processed.append(tuple(units))
        else:
            abort(400)

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
            abort(400)
        if not start_data[key]:
            abort(400)

    if not start_data['number'] or not stop_data['number']:
        abort(400)

    try:
        model = int(start_data['model'])
        start_num = int(start_data['number'])
        stop_num = int(stop_data['number'])
    except:
        abort(400)

    return (start_data['pdb'], model,
            (start_data['chain'], start_num, stop_num))


def ranges(data):
    if 'units' not in data:
        abort(400)
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
            abort(400)

        if data[1] != model:
            abort(400)

        ranges.append(data[2])

    return pdb, model, ranges
