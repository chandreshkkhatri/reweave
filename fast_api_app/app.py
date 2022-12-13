from typing import Union

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fast_api_app.routes import ping, video_requests

app = FastAPI()
app.include_router(ping.router)
app.include_router(video_requests.router)

origins = [
    "http://localhost",
    "http://localhost:3000",
    "http://localhost:8000",
    "https://witty-field-0ca482f10.2.azurestaticapps.net"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}
    