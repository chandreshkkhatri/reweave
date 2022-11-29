import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

taxis_media_db = mongo_client["t-axis-media"]

def get_mongo_client():
    return taxis_media_db