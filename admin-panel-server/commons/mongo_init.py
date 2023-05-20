from motor.motor_asyncio import AsyncIOMotorClient
from motor.motor_tornado import MotorDatabase
from commons.config import config

motor_client: AsyncIOMotorClient = None

async def connect_to_mongo():
    global motor_client
    if motor_client is None:
        motor_client = AsyncIOMotorClient(config.db_host)
    
async def get_db_client() -> AsyncIOMotorClient:
    global motor_client
    await connect_to_mongo()
    return motor_client

async def get_db() -> MotorDatabase:
    global motor_client
    await connect_to_mongo()
    return motor_client[config.db_name]
