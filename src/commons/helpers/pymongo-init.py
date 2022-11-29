import pymongo

mongo_client = pymongo.MongoClient("mongodb://localhost:27017/")

tg_content_db = mongo_client["tg_content_db"]
