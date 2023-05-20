from typing import List
from fastapi import APIRouter
from server_modules.controllers import video_template_controller
from server_modules.model.video_template import VideoTemplateModel

router = APIRouter()


@router.get("/video-templates", response_model=List[VideoTemplateModel])
async def get_all_templates():
    page = 0
    limit = 50
    templates = await video_template_controller.get_all_templates(page, limit)
    return templates


@router.get("/video-template/{id}", response_model=VideoTemplateModel)
async def get_template_by_id(id: str):
    template = await video_template_controller.get_template_by_id(id)
    return template


@router.post("/video-template")
async def create_template(template: VideoTemplateModel):
    return await video_template_controller.create_template(template)


@router.put("/video-template/{id}")
async def update_template(id: str, template: VideoTemplateModel):
    return await video_template_controller.update_template(id, template)


@router.delete("/video-template/{id}")
async def delete_template(id: str):
    return await video_template_controller.delete_template(id)
