"""This module contains the methods for generating output text formats for the
website.
"""

import csv
import cStringIO as sio

import simplejson as json

from flask import Response
from flask import render_template
from werkzeug.exceptions import BadRequest

from r3d2msa.alignments import write


def to_response(content, format_name=None):
    response = Response(content)

    if format_name:
        disposition = 'attachement; filename=alignment.%s' % format_name
        response.headers['Content-Disposition'] = disposition

    return response


def to_json(**kwargs):
    """Produce a json output. This will remove the 'template' key from the
    output as it is not something that needs to be publicly known.
    """

    if 'template' in kwargs:
        kwargs.pop('template')
    return to_response(json.dumps(kwargs), format_name='json')


def to_html(**kwargs):
    """Produce an HTML output. If this is given a template that is rendered. If
    not the status is used to select the correct template. If no status is
    given then the 'unknown' template is used.
    """

    status = kwargs.get('status', 'unknown')
    template = kwargs.get('template', 'results/%s.html' % status)
    return render_template(template, **kwargs)


def to_fasta(**kwargs):
    """Generate FASTA formatted output.
    """
    return to_response(write('fasta', kwargs), format_name='fasta')


def to_stockholm(**kwargs):
    """Generate stockholm formatted output.
    """
    return to_response(write('stockholm', kwargs), format_name='stockholm')


def to_clustal(**kwargs):
    """Generate clustal style output.
    """
    return to_response(write('clustal', kwargs), format_name='clustal')


def to_tsv(**kwargs):
    """Generate a TSV output. This will generete the variations as a TSV that
    can be imported to excel easily.
    """

    if 'full' not in kwargs:
        raise BadRequest("Can't generate TSV until processing is complete")

    handle = sio.StringIO()
    header = ['AccessionID', 'SeqVersion', 'CompleteFragment', 'TaxID',
              'ScientificName', 'LineageName']

    writer = csv.DictWriter(handle, header, delimiter='\t',
                            extrasaction='ignore')
    writer.writerow(dict(zip(header, header)))
    for row in kwargs['full']:
        writer.writerow(row)

    return to_response(handle.getvalue(), format_name='tsv')
