from fastapi import APIRouter
from fast_api_app.controllers import video_template_controller

router = APIRouter()


@router.get("/video-templates")
async def get_all_templates():
    page = 0
    limit = 50
    templates = await video_template_controller.get_all_templates(page, limit)
    return templates

@router.get("/video-template/{id}")
async def get_template_by_id(id: str):
    template = await video_template_controller.get_template_by_id(id)
    return template

@router.post("/video-template")
async def create_template(template: dict):
    return await video_template_controller.create_template(template)

@router.delete("/video-template/{id}")
async def delete_template(id: str):
    return await video_template_controller.delete_template(id)

    

