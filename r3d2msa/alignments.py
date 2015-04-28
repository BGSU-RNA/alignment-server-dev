"""This is a basic module that contains some logic for turning results from a
dictionary into sequence alignment text.
"""

import cStringIO as sio

from Bio import AlignIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_rna
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment

from werkzeug.exceptions import NotAcceptable


class NoAlignmentPossible(Exception):
    """This is if we cannot generate an alignment out of the data we are given.
    This can be the case if we are trying to create an alignment for something
    that has not yet been processed.
    """
    pass


def as_alignment(data):
    """Turn a result dictionary into a MultipleSeqAlignment that BioPython can
    write to a file. This requires the dictionary have a 'full' entry that is a
    list. The id entry for each sequence will the be the genbank id, while the
    description will be the ScientificName.

    :param dict data: The data dictionary to write.
    :returns: A MultipleSeqAlignment representing the result.
    """

    if 'full' not in data:
        raise NotAcceptable("Cannot create alignment until data is processed")

    sequences = []

    for entry in data['full']:
        seq = Seq(entry['CompleteFragment'], generic_rna)
        record = SeqRecord(seq)
        record.id = '%s.%s' % (entry['SeqID'], entry['SeqVersion'])
        record.description = entry['ScientificName']
        sequences.append(record)

    return MultipleSeqAlignment(sequences)


def write(name, data):
    """Write the result of the into a given file format. This will return a
    string that is the sequence alignment in data.

    :param string name: The name of the alignment format to use.
    :param dict data: The result to write.
    :returns A sequence alignment.
    """

    handle = sio.StringIO()
    alignment = as_alignment(data)
    AlignIO.write(alignment, handle, name)
    return handle.getvalue()
