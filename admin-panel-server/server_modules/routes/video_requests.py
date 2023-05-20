from typing import List
from fastapi import APIRouter, status
from fastapi.responses import JSONResponse
from server_modules.controllers import video_requests_controller
from fastapi.encoders import jsonable_encoder
from server_modules.model.video_request import VideoRequestModel
from commons.enums.templates import VideoTemplates

router = APIRouter()


@router.get("/video-request/{id}", response_model=VideoRequestModel)
async def get_video_request(id: str):
    resp = await video_requests_controller.get_video_request(id)
    if resp:
        return resp
    else:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content='Video request not found')


@router.post("/video-request")
async def create_video_request(videoRequest: VideoRequestModel):
    json_data = jsonable_encoder(videoRequest)
    return await video_requests_controller.create_request(json_data)


@router.delete("/video-request/{id}")
async def delete_video_request(id: str):
    return await video_requests_controller.delete_request(id)


@router.get("/video-requests", response_model=List[VideoRequestModel])
async def get_all_video_requests():
    page = 0
    limit = 50
    video_requests = await video_requests_controller.get_all_videos(page, limit)
    return video_requests


@router.get("/video-request/{id}/render")
async def render_video_request(id: str):
    return await video_requests_controller.render_request(id)


@router.get("/video-request/{id}/upload")
async def upload_video_request(id: str):
    return await video_requests_controller.upload_video(id)


@router.get("/types")
def get_types():
    """first route"""
    return "PONG"


@router.get('/template-names')
def get_templates():
    return [e.value for e in VideoTemplates]
