from flask import Flask
from flask_restful import reqparse
from flask_restful import Api, Resource
import time

from downloads_spotify.spotify_to_mp3 import process_downloads_spotify
from downloads_youtube.youtube_to_mp3 import process_downloads_youtube
def create_app():
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(HelloWorld, "/")
    api.add_resource(DownloadSpotify, "/downloads_spotify")
    api.add_resource(DownloadYoutube, "/downloads_youtube")

    return app


class HelloWorld(Resource):
    def get(self):
        return {"data": "Hello, my name is VNN"}


class GetData(Resource):
    def __init__(self):
        downloads_args = reqparse.RequestParser()
        # downloads_args.add_argument(
        #     "path", type=str, required=True, help="path missing",
        # )
        downloads_args.add_argument(
            "url_downloads", type=str, required=True, help="url_downloads missing"
        )
        self.downloads_args = downloads_args


class DownloadSpotify(GetData):
    def post(self):
        start_time = time.time()
        args = self.downloads_args.parse_args()
        try:
            process_downloads_spotify("data", args["url_downloads"])
            end_time = time.time()
            result = {
                "status": "success",
                "excution_time": str(end_time - start_time) + " second"
            }
        except Exception:
            result = {"status": "error", "data": ""}
        return result

class DownloadYoutube(GetData):
    def post(self):
        start_time = time.time()
        args = self.downloads_args.parse_args()
        try:
            process_downloads_youtube("data", args["url_downloads"])
            end_time = time.time()
            result = {
                "status": "success",
                "excution_time": str(end_time - start_time) + " second"
            }
        except Exception:
            result = {"status": "error", "data": ""}
        return result
    

app = create_app()

if __name__ == "__main__":
    create_app().run(port=8080)
