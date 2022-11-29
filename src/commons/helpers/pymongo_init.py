import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

tg_content_db = mongo_client["tg_content_db"]

def get_mongo_client():
    return tg_content_db