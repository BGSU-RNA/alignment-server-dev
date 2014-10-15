import os
import logging

from app import app

log_dir = os.path.join(os.path.realpath(__file__), "..", "logs")
if os.path.isdir(log_dir):
    handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)
