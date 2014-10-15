import os
import logging

from app import app

app_dir = os.path.dirname(os.path.realpath(__file__))
log_dir = os.path.realpath(os.path.join(app_dir, "..", "logs"))
if os.path.isdir(log_dir):
    handler = logging.FileHandler(os.path.join(log_dir, "app.log"))
    handler.setLevel(logging.INFO)
    app.logger.addHandler(handler)