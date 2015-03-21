"""This module contains the methods for generating output text formats for the
website.
"""

import simplejson as json

from flask import render_template

from r3d2msa.alignments import write


def to_json(**kwargs):
    """Produce a json output. This will remove the 'template' key from the
    output as it is not something that needs to be publicly known.
    """

    if 'template' in kwargs:
        kwargs.pop('template')
    return json.dumps(kwargs)


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
    return write('fasta', kwargs)


def to_stockholm(**kwargs):
    """Generate stockholm formatted output.
    """
    return write('stockholm', kwargs)


def to_clustal(**kwargs):
    """Generate clustal style output.
    """
    return write('clustal', kwargs)
