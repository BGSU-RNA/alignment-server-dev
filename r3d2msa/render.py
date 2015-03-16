import simplejson as json

from flask import render_template

from r3d2msa.alignments import write


def to_json(**kwargs):
    if 'template' in kwargs:
        kwargs.pop('template')
    return json.dumps(kwargs)


def to_html(**kwargs):
    status = kwargs.get('status', 'unknown')
    template = kwargs.get('template', 'results/%s.html' % status)
    return render_template(template, **kwargs)


def to_fasta(**kwargs):
    return write('fasta', kwargs)


def to_stockholm(**kwargs):
    return write('stockholm', kwargs)


def to_clustal(**kwargs):
    return write('clustal', kwargs)
