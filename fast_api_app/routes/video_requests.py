from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from fast_api_app.controllers import video_requests_controller
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
from src.commons.enums.templates import VideoTemplates

router = APIRouter()


class VideoRequest(BaseModel):
    template: str
    clips: list
    fileName: str
    uploadStatus: str = 'pending'
    renderStatus: str = 'pending'


@router.get("/video-request/{id}")
async def get_video_request(id: str):
    resp =  await video_requests_controller.get_video_request(id)
    if resp:
        return JSONResponse(status_code=status.HTTP_200_OK, content=resp)
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Video request not found')

@router.post("/video-request")
async def create_video_request(videoRequest: VideoRequest):
    json_data = jsonable_encoder(videoRequest)
    return await video_requests_controller.create_request(json_data)


@router.delete("/video-request/{id}")
async def delete_video_request(id: str):
    return await video_requests_controller.delete_request(id)


@router.get("/video-requests")
async def get_all_video_requests():
    page = 0
    limit = 50
    video_requests = await video_requests_controller.get_all_videos(page, limit)
    return JSONResponse(status_code=status.HTTP_200_OK, content=video_requests)


@router.get("/video-request/{id}/render")
async def render_video_request(id: str):
    return await video_requests_controller.render_request(id)


@router.get("/video-request/{id}/upload")
async def upload_video_request(id: str):
    return await video_requests_controller.upload_video(id)


@router.get("/video-request/{id}/cancel")
async def cancel_video_request(id: str):
    return await video_requests_controller.cancel_request(id)

@router.get("/types")
def get_types():
    """first route"""
    return "PONG"


@router.get('/template-names')
def get_templates():
    return [e.value for e in VideoTemplates]
