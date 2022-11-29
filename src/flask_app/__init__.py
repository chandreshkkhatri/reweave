"""
Module for the Flask application.
"""

from flask import Flask
from flask_cors import CORS
import commons.db as db
# from services.task_producer import create_bulk_video_request, create_video_request

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import src.flask_app.video
import src.flask_app.ping
import src.flask_app.data
