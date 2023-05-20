from server_modules.model.video_template import VideoTemplateCrudModel, VideoTemplateModel

async def get_all_templates(page, limit):
    """get all templates"""
    video_template_crud_model = VideoTemplateCrudModel()
    return await video_template_crud_model.get_all(page, limit)

async def get_template_by_id(id: str):
    """get template by id"""
    video_template_crud_model = VideoTemplateCrudModel()
    return await video_template_crud_model.get_by_id(id)

async def create_template(template: VideoTemplateModel):
    """create template"""
    video_template_crud_model = VideoTemplateCrudModel()
    return await video_template_crud_model.create(template)

async def update_template(id: str, template: VideoTemplateModel):
    """update template"""
    video_template_crud_model = VideoTemplateCrudModel()
    return await video_template_crud_model.update(id, template)

async def delete_template(id: str):
    """delete template"""
    video_template_crud_model = VideoTemplateCrudModel()
    return await video_template_crud_model.delete(id)
