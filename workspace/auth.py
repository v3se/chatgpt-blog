import requests
from flask import request, url_for
from client import client
import json

def get_google_provider_cfg():
    return requests.get('https://accounts.google.com/.well-known/openid-configuration').json()

def get_token(authorization_endpoint, code):
    token_url, headers, body = client.prepare_token_request(
        authorization_endpoint,
        authorization_response=request.url,
        redirect_url=request.base_url + url_for('login'),
        code=code
    )
    token_response = requests.post(
        token_url,
        headers=headers,
        data=body,
        auth=(client_id, client_secret),
    )
    client.parse_request_body_response(json.dumps(token_response.json()))

def get_user_info(userinfo_endpoint):
    uri, headers, body = client.add_token(userinfo_endpoint)
    userinfo_response = requests.get(uri, headers=headers, data=body)
    return userinfo_response.json()
