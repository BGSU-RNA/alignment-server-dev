#!/usr/bin/env python

import os
import sys
import json
import argparse

here = os.path.dirname(__file__)
sys.path.append(os.path.join(here, ".."))

from r3d2msa.db import rcad as db


def options(connection):
    pdbs, opts, tran = db.all_options(connection)

    alignments = {}
    for alignment in opts:
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
                'aln_fil': alignment['crw_aln_fil'],
                'option': alignment['option']
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


def main(config):
    connection = db.connect(config)
    data = options(connection)

    with open(config['options'], 'wb') as out:
        json.dump(data, out)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', default='conf/config.json',
                        help='Config file to use')
    args = parser.parse_args()

    with open(args.config, 'rb') as raw:
        config = json.load(raw)

    main(config)
