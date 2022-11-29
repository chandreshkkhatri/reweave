"""
Routes for video related endpoints.
"""
from flask import request
from flask_cors import cross_origin
from src.flask_app import app


@app.route('/video', methods=['POST'])
@cross_origin()
def video_request():
    """create video request"""
    if request.method == 'POST':
        data = request.json
        return data


@app.route('/cancel-video-request', methods=['GET'])
@cross_origin()
def cancel_video_request():
    """cancel video request"""
    if request.method == 'GET':
        return 'Video request cancelled'
