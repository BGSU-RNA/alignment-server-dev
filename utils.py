from flask import g
from flask import abort

import db

RANGE_LIMIT = 50


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


def full_range(start, end):
    # TODO: Implement me
    # TODO: Limit size of the range?
    return [start, end]


def get_sequences(units):
    # TODO: Implement this.
    pdb = '2AW7'
    model = 1
    ranges = units
    ranges = [('A', 887, 894)]
    return db.seqvar(g.seq_db, pdb, model, ranges)


def compute_variation(data):
    if 'units' not in data:
        abort(400)
    raw_units = data['units']
    units = parse_units(raw_units)
    variations = []
    for unit_range in units:
        full = full_range(*unit_range)
        variations = get_sequences(full)
        variations.append({
            'units': full,
            'range': unit_range,
            'sequences': get_sequences(units)
        })
    return variations
