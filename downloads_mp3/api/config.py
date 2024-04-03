import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()
CLIENT_ID = os.environ.get("CLIENT_ID", "input your client id here")
CLIENT_SECRET = os.environ.get("CLIENT_SECRET", "input your client secret here")
USERNAME = os.environ.get("USERNAME", "input your username here")
print(CLIENT_ID, CLIENT_SECRET, USERNAME)