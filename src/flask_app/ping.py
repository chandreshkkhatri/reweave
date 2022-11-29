"""
Test Route
"""
from src.flask_app import app


@app.route('/ping')
def hello_world():
    """first route"""
    return "PONG"
