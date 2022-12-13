"""
Server file
"""
import uvicorn
from fast_api_app.app import app

if __name__ == '__main__':
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
