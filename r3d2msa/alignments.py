import cStringIO as sio

from Bio import AlignIO
from Bio.Seq import Seq
from Bio.Alphabet import generic_rna
from Bio.SeqRecord import SeqRecord
from Bio.Align import MultipleSeqAlignment


class NoAlignmentPossible(Exception):
    """This is if we cannot generate an alignment out of the data we are given.
    This can be the case if we are trying to create an alignment for something
    that has not yet been processed.
    """
    pass


def as_alignment(data):
    if 'full' not in data:
        raise NoAlignmentPossible

    sequences = []
    for entry in data['full']:
        seq = Seq(entry['CompleteFragment'], generic_rna)
        record = SeqRecord(seq)
        record.id = '%s.%s' % (entry['AccessionID'], entry['SeqVersion'])
        record.description = entry['ScientificName']
        sequences.append(record)
    return MultipleSeqAlignment(sequences)


def write(name, data):
    handle = sio.StringIO()
    alignment = as_alignment(data)
    AlignIO.write(alignment, handle, name)
    return handle.getvalue()
