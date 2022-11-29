import json
from bson import json_util
from src.commons.helpers import get_mongo_client

mongo_client = get_mongo_client()
video_requests_table = mongo_client['video_requests']

def create_request(data):
    """create video request"""
    data = video_requests_table.insert_one(data)
    return data

def get_by_id(id):
    """get video requests"""
    video_requests = mongo_client['video_requests']
    return video_requests.find_one({
        'id': id
    })

def cancel_request(id):
    """cancel video request"""
    video_requests = mongo_client['video_requests']
    video_requests.update_one({
        'id': id,
        'status': 'pending'
    }, {
        '$set': {
            'status': 'cancelled'
        }
    })
    return 'Video request cancelled'

def get_all_videos(page, limit):
    """get all videos"""
    video_requests = mongo_client['video_requests']
    return video_requests.find({}).skip(page).limit(limit)

def update_video_request_status(id, status):
    """update video request status"""
    video_requests = mongo_client['video_requests']
    video_requests.update_one({
        'id': id
    }, {
        '$set': {
            'status': status
        }
    })
    return 'Video request status updated'

    