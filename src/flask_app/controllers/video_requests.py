from src.commons.helpers import get_mongo_client

mongo_client = get_mongo_client()

def create_request(request):
    """create video request"""
    data = request.json
    video_requests = mongo_client['video_requests']
    video_requests.insert_one(data)
    return data

def get_by_id(id):
    """get video requests"""
    video_requests = mongo_client['video_requests']
    return video_requests.find_one({id: id})

def cancel_request(id):
    """cancel video request"""
    video_requests = mongo_client['video_requests']
    video_requests.update_one({id: id, 'status': 'pending'}, {'status': 'cancelled'})
    return 'Video request cancelled'

def get_all_videos(page, limit):
    """get all videos"""
    video_requests = mongo_client['video_requests']
    return video_requests.find({}).skip(page).limit(limit)