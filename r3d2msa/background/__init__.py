"""The top level module for the queue and worker. This module also contains
sets which define the possible states of jobs.

Possible job statuses:
- pending: Placed in the queue waiting for a free worker.
- submitted: A worker is working on it.
- failed: The job failed for some reason.
- succeeded: The job was a success.

Jobs go from pending to submitted then either failed or succeeded.
"""

from . import queue
from . import worker

"""A set of possible status flags for jobs."""
KNOWN_STATUS = set(['pending', 'submitted', 'failed', 'succeeded'])

"""A set of job flags meaning the job is complete."""
FINISHED_STATUS = set(['failed', 'succeeded'])
