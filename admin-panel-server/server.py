"""
Server file
"""
# Importing the necessary modules
import uvicorn
from server_modules.app import app

# Checking if the script is run directly (not imported)
if __name__ == "__main__":
    # Running the server on host 0.0.0.0 and port 8000
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
