import os
import itertools as it
import collections as coll

import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import db
import utils as ut
import dummy_data as dd

import mimerender

app = Flask(__name__)
mimerender = mimerender.FlaskMimeRender()

render_json = lambda template, **kwargs: json.dumps(kwargs)
render_html = lambda template, **kwargs: render_template(template, **kwargs)


@app.before_request
def before_request():
    g.rcad = None
    if not app.debug:
        g.rcad = db.rcad_connect(app.config)


@app.teardown_request
def teardown_request(exception):
    db = getattr(g, 'rcad', None)
    if db is not None:
        db.close()


def variations(data):
    if app.debug:
        return dd.DATA

    pdb, model, ranges = ut.ranges(data)
    known = db.list_options(g.rcad)
    ut.validate(pdb, model, ranges, known)

    def translator(chain):
        return db.get_translation(g.rcad, pdb, model, chain)

    translated = ut.translate(translator, ranges)
    return db.seqvar(g.rcad, pdb, model, translated)


def options():
    if app.debug:
        return dd.LIST_OPTIONS
    return db.list_options(g.rcad)


def structures():
    if app.debug:
        return dd.LIST_STRUCTURES
    return db.list_structures(g.rcad)


def group_options():

    alignments = {}
    for alignment in options():
        description = alignment['description']
        pdb = alignment['pdb']
        if pdb not in alignments:
            alignments[pdb] = {}

        if description not in alignments[pdb]:
            alignments[pdb][description] = {
                'chains': [],
                'description': description,
                'alignment_id': description
            }
        info = alignments[pdb][description]
        info['chains'].append(alignment['chain_id'])

    data = []
    for structure in structures():
        entry = {}
        entry.update(structure)
        entry['alignments'] = alignments[structure['pdb']].values()
        entry['organism'] = entry['organism'].strip()
        entry['contents'] = entry['contents'].strip()
        entry['taxonomy'] = entry['taxonomy'].strip()

        if 'requires_translation' in entry:
            del entry['requires_translation']
        if 'option' in entry:
            del entry['option']

        data.append(entry)

    return data


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html
)
def get_html():
    if 'units' in request.args:
        full, summ, reqs = variations(request.args)
        return {'template': 'results.html', 'full': full, 'summ': summ, 'reqs': reqs}

    return {'template': 'form.html', 'data': group_options()}


@app.route('/', methods=['POST'])
@mimerender(
    json=render_json,
    html=render_html,
)
def post_html():
    data = request.get_json() or request.form
    return {'template': 'results.html', 'data': variations(data)}


if __name__ == '__main__':
    config = {}
    if os.path.exists('config.json'):
        with open('config.json', 'rb') as raw:
            config = json.load(raw)
    app.config.update(config)
    app.run()
