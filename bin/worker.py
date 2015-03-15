#!/usr/bin/env python

import os
import sys
import json
import argparse
import logging

here = os.path.dirname(__file__)
sys.path.append(os.path.abspath(os.path.join(here, "..")))

import r3d2msa.db.rcad as db
import r3d2msa.utils as ut
import r3d2msa.queue as q


class Worker(q.Worker):
    def process(self, query):
        rcad = db.connect(config)

        def translator(chain):
            return db.get_translation(rcad, query['pdb'], query['model'], chain)

        translated = ut.translate(translator, query['ranges'])
        full, summ, reqs = db.seqvar(rcad, query['pdb'], query['model'],
                                     translated)
        return {
            'id': query['id'],
            'units': query['units'],
            'full': full,
            'summ': summ,
            'reqs': reqs,
            'pdb': query['pdb'],
            'model': query['model'],
            'ranges': query['ranges']
        }


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config', dest='config', default='conf/config.json',
                        help='Config file to use')
    parser.add_argument('--log-file', dest='log_filename', default='',
                        help='File to log to')
    parser.add_argument('--name', dest='name', default='Worker',
                        help='Name of the worker for logging')
    args = parser.parse_args()

    if args.log_filename:
        logging.basicConfig(filename=args.log_filename)
    else:
        logging.basicConfig()

    with open(args.config, 'rb') as raw:
        config = json.load(raw)

    worker = Worker(config, name=args.name)
    worker()
