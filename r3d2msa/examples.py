import os
import glob
import hashlib


def filename(base, units):
    name = hashlib.md5(units).hexdigest()
    path = os.path.join(base, 'examples', name + '.json')
    return path


def load():
    examples = set()
    for filename in glob.glob("examples/*.json"):
        basename = os.path.basename(filename)
        name = os.path.splitext(basename)[0]
        examples.add(name)
    return examples


def known():
    return [
        {'description': 'Watson Crick Basepair',
         'units': '2AW7|1|A||1265,2AW7|1|A||1270'},
        {'description': 'GNRA Loop', 'units': '2AW7|1|A||1265:2AW7|1|A||1270'},
        {'description': 'Internal Loop',
         'units': '2AW7|1|A||580:2AW7|1|A||584,2AW7|1|A||757:2AW7|1|A||761'},
        {'description': 'Three way junction',
         'units': '2AW7|1|A||826:2AW7|1|A||829,2AW7|1|A||857:2AW7|1|A||861,2AW7|1|A||868:2AW7|1|A||874'}
    ]
