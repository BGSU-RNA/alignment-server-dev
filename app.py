import os
import hashlib

import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import db
import utils as ut
import examples

import mimerender


app = Flask(__name__)
mimerender = mimerender.FlaskMimeRender()

render_json = lambda template, **kwargs: json.dumps(kwargs)
render_html = lambda template, **kwargs: render_template(template, **kwargs)


@app.errorhandler(db.ProcessingException)
def handle_problem_range(error):
    return render_template('invalid_range.html'), 400


def options():
    with open('conf/options.json', 'rb') as raw:
        return json.load(raw)


def variations(data):
    name = hashlib.md5(data['units']).hexdigest()
    if name in app.config['examples']:
        filename = examples.filename(data['units'])
        with open(filename, 'rb') as raw:
            return json.load(raw)

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


def result(data):
    result = {'template': 'results.html'}
    result.update(variations(data))
    if app.config.get('log_queries'):
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

    return {
        'template': 'form.html',
        'examples': examples.known(),
        'data': options()
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


app.config['examples'] = examples.load()
config = {}
if os.path.exists('config.json'):
    with open('config.json', 'rb') as raw:
        config = json.load(raw)
app.config.update(config)


if __name__ == '__main__':
    app.run()
