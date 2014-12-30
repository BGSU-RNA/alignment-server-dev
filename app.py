import os
import glob
import hashlib

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


def load_examples():
    examples = set()
    for filename in glob.glob("examples/*.json"):
        basename = os.path.basename(filename)
        name = os.path.splitext(basename)[0]
        examples.add(name)
    return examples


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
    name = hashlib.md5(data['units']).hexdigest()
    if name in app.config['examples']:
        filename = os.path.join('examples', name + '.json')
        with open(filename, 'rb') as raw:
            data = json.load(raw)
            return data

    if app.debug:
        return dd.DATA

    pdb, model, ranges = ut.ranges(data)
    known = db.list_options(g.rcad)
    ut.validate(pdb, model, ranges, known)

    def translator(chain):
        return db.get_translation(g.rcad, pdb, model, chain)

    translated = ut.translate(translator, ranges)
    full, summ, reqs = db.seqvar(g.rcad, pdb, model, translated)
    return {
        'full': full,
        'summ': summ,
        'reqs': reqs,
        'pdb': pdb,
        'model': model,
        'ranges': ranges
    }


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


def result(data):
    result = {'template': 'results.html'}
    result.update(variations(data))
    if app.config['log_queries']:
        app.logger.info("Getting variations for: %s", data['units'])
    return result


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html,
    override_input_key='format',
)
def get_html():
    if 'units' in request.args:
        return result(request.args)

    return {'template': 'form.html', 'data': group_options()}


@app.route('/', methods=['POST'])
@mimerender(
    json=render_json,
    html=render_html,
    override_input_key='format',
)
def post_html():
    data = request.get_json() or request.form
    return result(data)


app.config['examples'] = load_examples()
config = {}
if os.path.exists('config.json'):
    with open('config.json', 'rb') as raw:
        config = json.load(raw)
app.config.update(config)


if __name__ == '__main__':
    app.run()
