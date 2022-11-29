"""
Module for the Flask application.
"""

from flask import Flask
from flask_cors import CORS
from flask.json import JSONEncoder
from bson import json_util

class CustomJSONEncoder(JSONEncoder):
    def default(self, obj): return json_util.default(obj)

app = Flask(__name__)
app.json_encoder = CustomJSONEncoder
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

import src.flask_app.ping
import src.flask_app.data
import src.flask_app.video
