# Admin Panel Server

This microservice provides an interface for administrators to manage the Videofy application.

## Dependencies

The admin-panel-server microservice requires the following dependencies:

- uvicorn
- fastapi

## Setup

To set up the admin-panel-server microservice, follow these steps:

1. Clone the repository to your local machine.
2. Navigate to the admin-panel-server directory.
3. Install the required dependencies using the command `pip install -r requirements.txt`.
4. Start the server using the command `python server.py`.

## Usage

The admin-panel-server microservice provides the following endpoints:

- `/admin`: This endpoint allows administrators to manage the application. The expected request and response formats are as follows:

  - Request: `GET /admin`
  - Response: `200 OK`
