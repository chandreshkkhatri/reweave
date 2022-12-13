import asyncio
from multiprocessing import Process
from fast_api_app.model import video_request_model
from src.services.video_builder.moviepy.creator import VideoCreator

rendering_in_progress = False

async def create_request(data):
    """create video request"""
    return await video_request_model.create_request(data)

async def get_video_request(id):
    """get video requests"""
    data = await video_request_model.get_by_id(id)
    if data:
        data['_id'] = str(data['_id'])
        return data
    return 

async def cancel_request(id):
    """cancel video request"""
    return await video_request_model.cancel_request(id)

async def get_all_videos(page, limit):
    """get all videos"""
    videos = await video_request_model.get_all_videos(page, limit)
    for video in videos:
        video['_id'] = str(video['_id'])
    return videos

async def render_request(id):
    """render video"""
    data = await video_request_model.get_by_id(id)
    global rendering_in_progress

    if data:
        if rendering_in_progress:
            return 'Another video is already being rendered'
        else:
            rendering_in_progress = True
            asyncio.create_task(render_video_in_parallel(data))
            return 'Video rendering started'
    return 'Video request not found'

async def render_video_in_parallel(data):
    """render video thread"""
    global rendering_in_progress
    video_creator = VideoCreator()
    video_creator.create_video_file(data.get('template'), data.get('clips'), data.get('fileName'))
    await video_request_model.update_render_status(data.get('_id'), 'complete')
    rendering_in_progress = False

async def upload_video(data):
    """upload video"""
    return await video_request_model.update_upload_status(data.get('_id'), 'complete')

async def delete_request(id):
    """delete video request"""
    return await video_request_model.delete_request(id)
