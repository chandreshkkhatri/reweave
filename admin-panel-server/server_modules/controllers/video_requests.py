from server_modules.model.video_request import RenderStatus, UploadStatus, VideoRequestCrudModel, VideoRequestModel
from microservices.rendering_services.video_builder import video_builder_controller

rendering_in_progress = False
ID = '_id'
TEMPLATE = 'template'
CLIPS = 'clips'
FILE_NAME = 'fileName'


async def create_request(data: VideoRequestModel):
    """create video request"""
    video_request_crud_model = VideoRequestCrudModel()
    await video_request_crud_model.create(data)
    return 'Video request created'


async def get_video_request(id: str):
    """get video requests"""
    video_request_crud_model = VideoRequestCrudModel()
    return await video_request_crud_model.get_by_id(id)


async def get_all_videos(page, limit):
    """get all videos"""
    video_request_crud_model = VideoRequestCrudModel()
    return await video_request_crud_model.get_all(page, limit)


async def render_request(id: str):
    """render video"""
    video_request_crud_model = VideoRequestCrudModel()
    data = await video_request_crud_model.get_by_id(id)
    global rendering_in_progress

    if data:
        if rendering_in_progress:
            return 'Another video is already being rendered'
        else:
            rendering_in_progress = True
            await render_video_in_parallel(VideoRequestModel.parse_obj(data))
            return 'Video rendering started'
    return 'Video request not found'


async def render_video_in_parallel(data: VideoRequestModel):
    """render video thread"""
    try:
        global rendering_in_progress
        await video_builder_controller.create_video_file(
            data.template, data.clips, data.fileName)
        video_request_crud_model = VideoRequestCrudModel()
        await video_request_crud_model.update_render_status(str(data.id), RenderStatus.complete.value)
    except Exception as e:
        print(e)
    rendering_in_progress = False


async def upload_video(data: VideoRequestModel):
    """upload video"""
    video_request_crud_model = VideoRequestCrudModel()
    return await video_request_crud_model.update_upload_status(data.id, UploadStatus.complete.value)


async def delete_request(id: str):
    """delete video request"""
    video_request_crud_model = VideoRequestCrudModel()
    return await video_request_crud_model.delete(id)
