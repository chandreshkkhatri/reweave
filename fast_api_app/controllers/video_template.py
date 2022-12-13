from fast_api_app.model import video_template_model

async def get_all_templates(page, limit):
    """get all templates"""
    templates = await video_template_model.get_all(page, limit)
    for template in templates:
        template['_id'] = str(template['_id'])
    return templates

async def get_template_by_id(id: str):
    """get template by id"""
    template = await video_template_model.get_by_id(id)
    template['_id'] = str(template['_id'])
    return template

async def create_template(template: dict):
    """create template"""
    return await video_template_model.create(template)

async def delete_template(id: str):
    """delete template"""
    return await video_template_model.delete(id)
