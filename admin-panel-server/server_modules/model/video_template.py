from typing import List, Optional
from bson.objectid import ObjectId
from server_modules.model.base_crud_model import BaseCrudModel
from commons import get_db
from pydantic import BaseModel, Field

from commons.classes.py_object_id import PyObjectId

VIDEO_TEMPLATES = 'video_templates'
ID = '_id'
STANDARD_SHORT_ASPECT_RATIO = (900, 1600)
WHITE_COLOR = (0, 0, 0)


class VideoTemplateModel(BaseModel):
    """Class for Initializing a template for a video"""
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    font_color: str
    font_family: str
    font_size: int
    title_font_size: str
    background_image: Optional[str]
    background_color: str
    text_clip_method: str
    text_clip_color_pos: str
    background_audio: str
    use_background_image: bool
    terminal_clip_audio: str
    cover_image: Optional[str] = ''
    duration: int = 30
    title_clip_duration: int = 5
    end_clip_duration: int = 5
    subclip_duration: int = 5
    cover_font_size: int = 100
    aspect_ratio: str = 'shorts'
    text_background_color = WHITE_COLOR

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class VideoTemplateCrudModel(BaseCrudModel):
    """Class for CRUD operations on video templates"""

    def __init__(self):
        super().__init__(VideoTemplateModel, VIDEO_TEMPLATES)

    async def get_by_name(self, name) -> VideoTemplateModel:
        """get a video template by name"""
        mongo_db = await get_db()
        video_templates_collection = mongo_db.get_collection(VIDEO_TEMPLATES)
        template = await video_templates_collection.find_one({"name": name})
        if template:
            template[ID] = str(template[ID])
        return template
