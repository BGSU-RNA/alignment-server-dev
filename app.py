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


@app.errorhandler(db.ProcessingException)
def handle_problem_range(error):
    return render_template('invalid_range.html'), 400


def example_filename(units):
    name = hashlib.md5(units).hexdigest()
    path = os.path.join(os.path.abspath(os.path.dirname(__file__)),
                        'examples', name + '.json')
    return path


def variations(data):
    name = hashlib.md5(data['units']).hexdigest()
    if name in app.config['examples']:
        filename = example_filename(data['units'])
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


def configure():
    #   Needs a fully-tested and viable debugging option... this should be partway there.
    if app.debug:
        return dd.LIST_STRUCTURES, dd.LIST_OPTIONS
    return db.all_options(g.rcad)


def group_options():
    pdbs, opts, tran = configure()

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


def result(data):
    result = {'template': 'results.html'}
    result.update(variations(data))
    if app.config.get('log_queries'):
        app.logger.info("Getting variations for: %s", data['units'])
    return result


def examples():
    return [
        {'description': 'Watson Crick Basepair',
         'units': '2AW7|1|A||1265,2AW7|1|A||1270'},
        {'description': 'GNRA Loop', 'units': '2AW7|1|A||1265:2AW7|1|A||1270'},
        {'description': 'Internal Loop',
         'units': '2AW7|1|A||580:2AW7|1|A||584,2AW7|1|A||757:2AW7|1|A||761'},
        {'description': 'Three way junction',
         'units': '2AW7|1|A||826:2AW7|1|A||829,2AW7|1|A||857:2AW7|1|A||861,2AW7|1|A||868:2AW7|1|A||874'}
    ]


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html,
    override_input_key='format',
)
def get_html():
    if 'units' in request.args:
        return result(request.args)

    return {
        'template': 'form.html',
        'examples': examples(),
        'data': group_options()
    }


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
