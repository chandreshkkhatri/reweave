
from commons.mongo_init import get_db
from pydantic import BaseModel, Field
from bson.objectid import ObjectId

ID = '_id'


class BaseCrudModel:
    def __init__(self, model, collection_name):
        self.model = model
        self.collection_name = collection_name

    async def create(self, data):
        """create a video template"""
        mongo_db = await get_db()
        collection = mongo_db.get_collection(self.collection_name)
        await collection.insert_one(data)
        return True

    async def get_by_id(self, id):
        """get a video template by id"""
        mongo_db = await get_db()
        collection = mongo_db.get_collection(self.collection_name)
        response = await collection.find_one({ID: id})
        return response

    async def get_all(self, page, limit):
        """get all video templates"""
        mongo_db = await get_db()
        collection = mongo_db.get_collection(self.collection_name)
        response = await collection.find().skip(page).limit(limit).to_list(length=limit)
        return response

    async def update(self, id, data):
        """update a video template"""
        mongo_db = await get_db()
        collection = mongo_db.get_collection(self.collection_name)
        return await collection.update_one({ID: ObjectId(id)}, {'$set': data})

    async def delete(self, id):
        """delete a video template by id"""
        mongo_db = await get_db()
        collection = mongo_db.get_collection(self.collection_name)
        return await collection.delete_one({ID: ObjectId(id)})
