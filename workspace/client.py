from oauthlib.oauth2 import WebApplicationClient
import os

client = WebApplicationClient(os.environ.get('GOOGLE_CLIENT_ID'))
