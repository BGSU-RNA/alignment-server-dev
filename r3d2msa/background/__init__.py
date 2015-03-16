from . import queue
from . import worker

KNOWN_STATUS = set(['pending', 'submitted', 'failed', 'succeeded'])
FINISHED_STATUS = set(['failed', 'succeeded'])
