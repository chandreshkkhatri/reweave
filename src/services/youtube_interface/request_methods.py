# -*- coding: utf-8 -*-

# Sample Python code for youtube.channels.list
# See instructions for running these code samples locally:
# https://developers.google.com/explorer-help/code-samples#python

# import os

import googleapiclient.discovery
from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials

from googleapiclient.http import MediaFileUpload
from src.commons.redis_init import redis_conn
hname = 'yt_session'
yt_session_token_key = 'yt_session_token'


class YouTubeClient:
    def __init__(self):
        # os.environ["OAUTHLIB_RELAX_TOKEN_SCOPE"] = '1'
        # os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"
        cached_session_token = redis_conn.hget(
            name=hname, key=yt_session_token_key)
        if cached_session_token:
            credentials = Credentials(cached_session_token.decode('utf-8'))
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json',
                scopes=['https://www.googleapis.com/auth/youtube'])

            flow.run_local_server()
            credentials = flow.credentials
            redis_conn.hset(name=hname, key=yt_session_token_key,
                            value=credentials.token)

        api_service_name = "youtube"
        api_version = "v3"
        # cred_file = open('gapi_cred.json')
        # data = json.load(cred_file)
        # DEVELOPER_KEY = data['key']
        # cred_file.close()

        self.youtube = googleapiclient.discovery.build(
            api_service_name, api_version, credentials=credentials)

    def delete_video(self, id):
        # Disable OAuthlib's HTTPS verification when running locally.
        # *DO NOT* leave this option enabled in production.
        request = self.youtube.videos().delete(id=id)
        response = request.execute()
        print(response)

    def upload_video(self, file_name, title):
        request = self.youtube.videos().insert(
            part='snippet',
            body={
                "kind": "youtube#video",
                "snippet": {
                    "title": title
                }
            },
            media_body=MediaFileUpload(f'builds/{file_name}')
        )
        response = request.execute()
        print(response)
