import os
import sys
import logging

sys.path.append(os.path.dirname(__file__))

from app import app as application

logging.basicConfig(stream=sys.stdout)
