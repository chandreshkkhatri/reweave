from multiprocessing import Process
from src.flask_app.model import video_request_model
from src.services.video_builder.moviepy.creator import VideoCreator

rendering_in_progress = False

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

def render_video(id):
    """render video"""
    data = video_request_model.get_by_id(id)
    global rendering_in_progress

    if data:
        if rendering_in_progress:
            return 'Another video is already being rendered'
        else:
            rendering_in_progress = True
            process = Process(target=render_video_in_parallel, args=(data,))
            process.start()
            return 'Video rendering started'
    return 'Video request not found'

def render_video_in_parallel(data):
    """render video thread"""
    global rendering_in_progress
    video_creator = VideoCreator()
    video_creator.create_video_file(data.get('template'), data.get('clips'), data.get('fileName'))
    video_request_model.update_render_status(data.get('_id'), 'complete')
    rendering_in_progress = False
