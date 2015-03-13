#!/usr/bin/env python

import os
import sys
import json

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, ".."))

import db


def options(connection):
    pdbs, opts, tran = db.all_options(connection)

    alignments = {}
    for alignment in opts:
        print(alignment)
        description = alignment['description']
        pdb = alignment['pdb']
        if pdb not in alignments:
            alignments[pdb] = {}

        if description not in alignments[pdb]:
            alignments[pdb][description] = {
                'chains': [],
                'description': description,
                'alignment_id': description,
                'diagram': alignment['crw_diagram'],
                'aln_dir': alignment['crw_aln_dir'],
                'aln_fil': alignment['crw_aln_fil']
            }
        info = alignments[pdb][description]
        info['chains'].append(alignment['chain_id'])

    data = []
    for structure in pdbs:
        entry = {}
        entry.update(structure)
        entry['alignments'] = alignments[structure['pdb']].values()

        if 'requires_translation' in entry:
            del entry['requires_translation']
        if 'option' in entry:
            del entry['option']

        data.append(entry)

    return data


def main(config, filename):
    connection = db.rcad_connect(config)
    data = options(connection)

    with open(filename, 'wb') as out:
        json.dump(data, out)


if __name__ == '__main__':
    main({}, 'conf/options.json')
