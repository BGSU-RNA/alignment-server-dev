import cStringIO as sio

from Bio import AlignIO


def as_alignment(data):
    pass


def write(name, data):
    handle = sio.StringIO
    alignment = as_alignment(data)
    AlignIO.write(alignment, handle, name)
    return handle.get_value()


def writer(name):
    def func(data):
        write(name, data)
    return writer
