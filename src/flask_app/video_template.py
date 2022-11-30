from flask import request
from flask_cors import cross_origin
from src.flask_app import app
from src.flask_app.model import video_template_model

@app.route('/video-template', methods=['GET','POST'])
@cross_origin()
def templates():
    """templates methods"""
    if request.method == 'POST':
        data = request.json
        return video_template_model.create(data)

@app.route('/video-template/<id>', methods=['GET','DELETE'])
@cross_origin()
def templates_by_id(id):
    """templates methods"""
    if request.method == 'GET':
        return video_template_model.get_by_id(id)
    if request.method == 'DELETE':
        return video_template_model.delete(id)

@app.route('/video-templates', methods=['GET'])
@cross_origin()
def get_all_templates():
    """get all templates"""
    if request.method == 'GET':
        page = 0
        limit = 50
        if 'page' in request.args:
            page = int(request.args['page'])
        if 'limit' in request.args:
            limit = int(request.args['limit'])
        return video_template_model.get_all(page, limit)        
