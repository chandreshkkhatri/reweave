from bson.objectid import ObjectId
from src.commons.helpers import get_mongo_client

video_templates_collection = get_mongo_client().video_templates

def create(data):
    """create a video template"""
    return video_templates_collection.insert_one(data).inserted_id

def get_by_id(id):
    """get a video template by id"""
    return video_templates_collection.find_one({'_id': ObjectId(id)})

def delete(id):
    """delete a video template by id"""
    return video_templates_collection.delete_one({'_id': ObjectId(id)})

def get_all(page, limit):
    """get all video templates"""
    return video_templates_collection.find().skip(page * limit).limit(limit)