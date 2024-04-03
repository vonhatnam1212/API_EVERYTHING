import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
from youtube_search import YoutubeSearch
import multiprocessing
import urllib.request
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
import json
from config import CLIENT_ID, CLIENT_SECRET, USERNAME
from utils import generate_path

auth_manager = oauth2.SpotifyClientCredentials(
    client_id=CLIENT_ID, client_secret=CLIENT_SECRET
)
spotify = spotipy.Spotify(auth_manager=auth_manager)


def save_file_metadata(record, file_path):
    try:
        # Tách đường dẫn và tên file
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            # Nếu không tồn tại, tạo các thư mục cha
            os.makedirs(directory)
        with open(file_path, "a") as f:
            json.dump(record, f)
            f.write(os.linesep)
    except:
        print("error with ", record)


def write_playlist_dowloads_mp3(text_file: str, tracks: dict):
    # This includins the name, artist, and spotify URL. Each is delimited by a comma.
    while True:
        for item in tracks["items"]:
            if "track" in item:
                track = item["track"]
            else:
                track = item
            write_track_dowloads_mp3(text_file, track)
        # 1 page = 50 results, check if there are more pages
        if tracks["next"]:
            tracks = spotify.next(tracks)
        else:
            break


def write_track_dowloads_mp3(text_file: str, track: dict):
    directory = os.path.dirname(text_file)
    if not os.path.exists(directory):
        # Nếu không tồn tại, tạo các thư mục cha
        os.makedirs(directory)
    with open(text_file, "a", encoding="utf-8") as file_out:
        try:
            track_url = track["external_urls"]["spotify"]
            track_name = track["name"]
            track_artist = track["artists"][0]["name"]
            if track["external_urls"]["spotify"].split("/")[-2] == "album":
                album_art_url = track["images"][0]["url"]
            else:
                album_art_url = track["album"]["images"][0]["url"]
            csv_line = (
                track_name
                + ","
                + track_artist
                + ","
                + track_url
                + ","
                + album_art_url
                + "\n"
            )
            try:
                file_out.write(csv_line)
            except UnicodeEncodeError:  # Most likely caused by non-English song names
                print(
                    "Track named {} failed due to an encoding error. This is \
                            most likely due to this song having a non-English name.".format(
                        track_name
                    )
                )
        except KeyError:
            print(
                "Skipping track {0} by {1} (local only?)".format(
                    track["name"], track["artists"][0]["name"]
                )
            )


def write_playlist(playlist_id: str):

    results = spotify.playlist(playlist_id)
    playlist_name = results["name"]
    print(os.getcwd())
    save_file_metadata(results, "metadata/{}.txt".format(playlist_name))
    text_file = "data/{0}.txt".format(playlist_name)
    print("Writing {0} tracks to {1}.".format(results["tracks"]["total"], text_file))
    tracks = results["tracks"]
    write_playlist_dowloads_mp3(text_file, tracks)

    return playlist_name

def write_track(track_id: str):

    results = spotify.track(track_id)
    track_name = results["name"]
    print(os.getcwd())
    save_file_metadata(results, "metadata/{}.txt".format(track_name))
    text_file = "data/{0}.txt".format(track_name)
    # print("Writing {0} tracks to {1}.".format(results["tracks"]["total"], text_file))
    track = results
    write_track_dowloads_mp3(text_file, track)

    return track_name

def write_album(album_id: str):

    results = spotify.album(album_id)
    album_name = results["name"]
    print(os.getcwd())
    save_file_metadata(results, "metadata/{}.txt".format(album_name))
    text_file = "data/{0}.txt".format(album_name)
    # print("Writing {0} tracks to {1}.".format(results["tracks"]["total"], text_file))
    track = results
    write_track_dowloads_mp3(text_file, track)

    return album_name

