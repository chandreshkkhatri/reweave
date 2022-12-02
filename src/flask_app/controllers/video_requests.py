from src.flask_app.model import video_request_model

def create_request(data):
    """create video request"""
    data['renderStatus'] = 'pending'
    data['uploadStatus'] = 'pending'
    return video_request_model.create_request(data)

def get_video_request(id):
    """get video requests"""
    data = video_request_model.get_by_id(id)
    if data:
        return data
    return 'Video request not found'

def cancel_request(id):
    """cancel video request"""
    return video_request_model.cancel_request(id)

def get_all_videos(page, limit):
    """get all videos"""
    return video_request_model.get_all_videos(page, limit)
