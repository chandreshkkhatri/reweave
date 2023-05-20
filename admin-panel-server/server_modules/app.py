
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from server_modules.routes import ping, video_requests, video_template
from commons.config import config
from commons.mongo_init import connect_to_mongo, get_db_client, get_db
from dotenv import load_dotenv
 
app = FastAPI()
app.include_router(ping.router)
app.include_router(video_requests.router)
app.include_router(video_template.router)

origins = [
    config.local_fe_host,
    config.production_fe_host,
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    load_dotenv()
    await connect_to_mongo()
    app.mongo_client = get_db_client()
    app.mongo_db = get_db()

@app.on_event("shutdown")
async def shutdown_event():
    app.mongo_client.close()

@app.get("/")
def read_root():
    return {"Hello": "World"}
    