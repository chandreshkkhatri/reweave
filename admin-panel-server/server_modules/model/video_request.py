from enum import Enum
from typing import Optional
from bson.objectid import ObjectId
from server_modules.model.base_crud_model import BaseCrudModel
from commons import get_db
from pydantic import BaseModel, Field

from microservices.commons.classes.py_object_id import PyObjectId

VIDEO_REQUESTS = 'video_requests'
ID = '_id'
RENDER_STATUS = 'renderStatus'
UPLOAD_STATUS = 'uploadStatus'


class UploadStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    complete = 'complete'
    failed = 'failed'


class RenderStatus(str, Enum):
    pending = 'pending'
    in_progress = 'in_progress'
    complete = 'complete'
    failed = 'failed'


class VideoRequestModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias='_id')
    template: str
    clips: list
    fileName: str
    uploadStatus: str = UploadStatus.pending
    renderStatus: str = RenderStatus.pending

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            ObjectId: str
        }


class VideoRequestCrudModel(BaseCrudModel):
    def __init__(self):
        super().__init__(VideoRequestModel, VIDEO_REQUESTS)

    async def update_render_status(self, id: str, status: RenderStatus):
        mongo_db = await get_db()
        video_requests_collection = mongo_db[VIDEO_REQUESTS]
        await video_requests_collection.update_one({
            ID: id
        }, {
            '$set': {
                RENDER_STATUS: status
            }
        })
        return 'Video request render status updated'

    async def update_upload_status(self, id: str, status: UploadStatus):
        """update video request status"""
        mongo_db = await get_db()
        video_requests_collection = mongo_db[VIDEO_REQUESTS]
        await video_requests_collection.update_one({
            ID: id
        }, {
            '$set': {
                UPLOAD_STATUS: status
            }
        })
        return 'Video request upload status updated'
