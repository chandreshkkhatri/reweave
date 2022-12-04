from bson.objectid import ObjectId
from src.commons.helpers import get_mongo_client

mongo_client = get_mongo_client()
video_requests_table = mongo_client['video_requests']


def create_request(data):
    """create video request"""
    try:
        video_requests_table.insert_one(data)
        return 'Video request created'
    except Exception as e:
        print(e)
        return 'Video request not created'


def get_by_id(id):
    """get video requests"""
    return video_requests_table.find_one({
        '_id': ObjectId(id)
    })


def cancel_request(id):
    """cancel video request"""
    video_requests_table.update_one({
        '_id': ObjectId(id),
        'status': 'pending'
    }, {
        '$set': {
            'status': 'cancelled'
        }
    })
    return 'Video request cancelled'


def get_all_videos(page, limit):
    """get all videos"""
    cursor = video_requests_table.find().skip(page*limit).limit(limit)
    return list(cursor)

def update_render_status(id, status):
    video_requests_table.update_one({
        '_id': ObjectId(id)
    }, {
        '$set': {
            'renderStatus': status
        }
    })
    return 'Video request render status updated'
    

def update_video_request_status(id, status):
    """update video request status"""
    video_requests = mongo_client['video_requests']
    video_requests.update_one({
        'id': ObjectId(id)
    }, {
        '$set': {
            'status': status
        }
    })
    return 'Video request status updated'
