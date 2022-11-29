"""
Routes for data related endpoints.
"""
from flask_cors import cross_origin
from src.flask_app import app
from commons.enums.templates import VideoTemplates


@app.route('/types', methods=['GET'])
@cross_origin()
def get_types():
    """first route"""
    return "PONG"


@app.route('/templates', methods=['GET'])
@cross_origin()
def get_templates():
    return [e.value for e in VideoTemplates]
