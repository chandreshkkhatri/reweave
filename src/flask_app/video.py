"""
Routes for video related endpoints.
"""
from flask import request
from flask_cors import cross_origin
from src.commons.helpers import get_mongo_client
from src.flask_app.controllers import video_requests_controller
from src.flask_app import app
mongo_client = get_mongo_client()

@app.route('/video', methods=['GET','POST'])
@cross_origin()
def video_request():
    """video request methods"""
    if request.method == 'POST':
        data = request.json
        video_requests_controller.create_request(data)
        return data

@app.route('/video/<id>', methods=['GET','DELETE'])
@cross_origin()
def video_request_by_id(id):
    """video request methods"""
    if request.method == 'GET':
        return video_requests_controller.get_video_request(id)
    if request.method == 'DELETE':
        return video_requests_controller.cancel_request(id)

@app.route('/cancel-video-request', methods=['GET'])
@cross_origin()
def cancel_video_request():
    """cancel video request"""
    if request.method == 'GET':
        data = request.json
        id = data['id']
        return video_requests_controller.cancel_request(id)

@app.route('/get-all-videos', methods=['GET'])
@cross_origin()
def get_all_videos():
    print('get all videos')
    """get all videos"""
    if request.method == 'GET':
        page = 0
        limit = 50
        return video_requests_controller.get_all_videos(page, limit)

