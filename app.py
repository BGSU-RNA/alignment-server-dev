import os
import hashlib

import simplejson as json

from flask import g
from flask import Flask
from flask import request
from flask import render_template

import r3d2msa as r3d

import mimerender


app = Flask(__name__)

mimerender.register_mime('fasta', ('text/fasta',))
# mimerender.register_mime('stockholm', ('text/stockholm',))
mimerender.register_mime('clustal', ('text/clustal',))
mimerender = mimerender.FlaskMimeRender()


def render_json(**kwargs):
    if 'template' in kwargs:
        kwargs.pop('template')
    return json.dumps(kwargs)


def render_html(**kwargs):
    status = kwargs.get('status', 'unknown')
    template = kwargs.get('template', 'results/%s.html' % status)
    return render_template(template, **kwargs)


def options():
    with open(app.config['options'], 'rb') as raw:
        return json.load(raw)


def known():
    """Generate a list of all known pdbs, models and chains we allow.
    """

    known = []
    for option in options():
        for alignment in option['alignments']:
            for chain in alignment['chains']:
                known.append({
                    'pdb': option['pdb'],
                    'model_number': option['model_number'],
                    'chain_id': chain
                })
    return known


def create_id(data):
    """Should create an id that is unique the query, but this should be the
    same given the same inputs. Here we use an md5 of the requested units to do
    this. In the future, if we support multiple alignments per chain we should
    use units and the alignment id.

    :param dict data: The query we are getting an id for.
    :returns: An id string for the query.
    """

    md5 = hashlib.md5()
    md5.update(data['units'])
    return md5.hexdigest()


def create_query(data):
    """Turn the requested ata into a proper query. This validates the data to
    make sure it is valid and then builds the query data structure. We hold off
    on translating this as that requires a connection to rcad. We want to
    connect to rcad outside the web server to prevent slow downs due to
    connection issues.

    :param dict data: The dictionary to generate a query from.
    :returns: The query dict. This will contain a pdb, models and ranges key.
    The values here are the ones produced by parsing the units entry of the
    data dictonary with r3d2msa.utils.ranges. We also add an id entry, which is
    an id unique to this query as produced by create_id. It also has the
    'units' entry from the given data.
    """

    pdb, model, ranges = r3d.utils.ranges(data)
    r3d.utils.validate(pdb, model, ranges, known())

    query = {
        'pdb': pdb,
        'model': model,
        'ranges': ranges,
        'units': data['units']
    }
    query['id'] = create_id(query)
    return query


def result(data):
    """Determine the result, if any of the query. This will ask the current
    queue for the status of the query. If it is finshed either successfully or
    not it will get the result and return it. If this query has not yet been
    submitted then it will submit the query and set the status to submitted.

    :param dict data: The data to get a result for.
    :returns: A dictonary representing the result. This will have a status key.
    The status is a string in the KNOWN_STATUS set from r3d2msa.queue. If the
    status is one of the finished statuses then the dictonary will also include
    all keys from loading the result.
    """

    query = create_query(data)
    queue = g.queue
    status = queue.status(query)

    result = {}
    if status in r3d.queue.KNOWN_STATUS:
        result['status'] = status
    else:
        queue.submit(query)
        result['status'] = 'submitted'

    if status in r3d.queue.FINISHED_STATUS:
        result.update(queue.result(query))

    return result


@app.before_request
def before_request():
    g.queue = r3d.queue.Queue(app.config)


@app.route('/', methods=['GET'])
@mimerender(
    json=render_json,
    html=render_html,
    fasta=r3d.alignments.fasta,
    # stockholm=r3d.alignments.stockholm,
    clustal=r3d.alignments.clustal,
    override_input_key='format',
)
def get_data():
    if 'units' in request.args:
        return result(request.args)

    return {
        'template': 'form.html',
        'examples': r3d.examples.known(),
        'data': options()
    }


@app.route('/', methods=['POST'])
@mimerender(
    json=render_json,
    html=render_html,
    fasta=r3d.alignments.fasta,
    # stockholm=r3d.alignments.stockholm,
    clustal=r3d.alignments.clustal,
    override_input_key='format',
)
def post_data():
    data = request.get_json() or request.form
    return result(data)


here = os.path.abspath(os.path.dirname(__file__))
config_path = os.path.join('conf', 'config.json')
with open(config_path, 'rb') as raw:
    app.config.update(json.load(raw))


if __name__ == '__main__':
    app.run()
