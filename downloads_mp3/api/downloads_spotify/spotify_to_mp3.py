# Downloads a Spotify playlist into a folder of MP3 tracks
# Jason Chen, 21 June 2020

import os
import spotipy
import spotipy.oauth2 as oauth2
import yt_dlp
from youtube_search import YoutubeSearch
import multiprocessing
import urllib.request
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC, error
from downloads_spotify.write_track_spotify import write_playlist, write_track, write_album
import sys
from config import CLIENT_ID, CLIENT_SECRET, USERNAME
from utils import generate_path



def find_and_download_songs(reference_file: str):
    TOTAL_ATTEMPTS = 20
    with open(reference_file, "r", encoding="utf-8") as file:
        for line in file:
            temp = line.split(",")
            name, artist, album_art_url = temp[0], temp[1], temp[3]
            text_to_search = artist + " - " + name
            best_url = None
            attempts_left = TOTAL_ATTEMPTS
            while attempts_left > 0:
                try:
                    results_list = YoutubeSearch(
                        text_to_search, max_results=1
                    ).to_dict()
                    best_url = "https://www.youtube.com{}".format(
                        results_list[0]["url_suffix"]
                    )
                    break
                except IndexError:
                    attempts_left -= 1
                    print(
                        "No valid URLs found for {}, trying again ({} attempts left).".format(
                            text_to_search, attempts_left
                        )
                    )
            if best_url is None:
                print(
                    "No valid URLs found for {}, skipping track.".format(text_to_search)
                )
                continue

            print("Initiating download for Image {}.".format(album_art_url))
            f = open("{}.jpg".format(name), "wb")
            f.write(urllib.request.urlopen(album_art_url).read())
            f.close()

            # Run you-get to fetch and download the link's audio
            print("Initiating download for {}.".format(text_to_search))
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": "%(title)s",  # name the file the ID of the video
                "embedthumbnail": True,
                "postprocessors": [
                    {
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "mp3",
                        "preferredquality": "192",
                    },
                    {
                        "key": "FFmpegMetadata",
                    },
                ],
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info([best_url][0], download=True)

                # extract the name of the downloaded file from the info_dict
            filename = ydl.prepare_filename(info_dict)
            print(f"The downloaded file name is: {filename}")

            print("AddingCoverImage ...")
            audio = MP3(f"{filename}" + ".mp3", ID3=ID3)
            try:
                audio.add_tags()
            except error:
                pass

            audio.tags.add(
                APIC(
                    encoding=3,  # 3 is for utf-8
                    mime="image/jpeg",  # can be image/jpeg or image/png
                    type=3,  # 3 is for the cover image
                    desc="Cover",
                    data=open("{}.jpg".format(name), mode="rb").read(),
                )
            )
            audio.save()
            os.remove("{}.jpg".format(name))


# Multiprocessed implementation of find_and_download_songs
# This method is responsible for manging and distributing the multi-core workload
def multicore_find_and_download_songs(reference_file: str, cpu_count: int):
    # Extract songs from the reference file

    lines = []
    with open(reference_file, "r", encoding="utf-8") as file:
        for line in file:
            lines.append(line)

    # Process allocation of songs per cpu
    number_of_songs = len(lines)
    songs_per_cpu = number_of_songs // cpu_count

    # Calculates number of songs that dont evenly fit into the cpu list
    # i.e. 4 cores and 5 songs, one core will have to process 1 extra song
    extra_songs = number_of_songs - (cpu_count * songs_per_cpu)

    # Create a list of number of songs which by index allocates it to a cpu
    # 4 core cpu and 5 songs [2, 1, 1, 1] where each item is the number of songs
    #                   Core 0^ 1^ 2^ 3^
    cpu_count_list = []
    for cpu in range(cpu_count):
        songs = songs_per_cpu
        if cpu < extra_songs:
            songs = songs + 1
        cpu_count_list.append(songs)

    # Based on the cpu song allocation list split up the reference file
    index = 0
    file_segments = []
    for cpu in cpu_count_list:
        right = cpu + index
        segment = lines[index:right]
        index = index + cpu
        file_segments.append(segment)

    # Prepares all of the seperate processes before starting them
    # Pass each process a new shorter list of songs vs 1 process being handed all of the songs
    processes = []
    segment_index = 0
    for segment in file_segments:
        p = multiprocessing.Process(
            target=multicore_handler, args=(segment, segment_index)
        )
        processes.append(p)
        segment_index = segment_index + 1

    # Start the processes
    for p in processes:
        p.start()

    # Wait for the processes to complete and exit as a group
    for p in processes:
        p.join()


# Just a wrapper around the original find_and_download_songs method to ensure future compatibility
# Preserves the same functionality just allows for several shorter lists to be used and cleaned up
def multicore_handler(reference_list: list, segment_index: int):
    # Create reference filename based off of the process id (segment_index)
    reference_filename = "{}.txt".format(segment_index)

    # Write the reference_list to a new "reference_file" to enable compatibility
    with open(reference_filename, "w+", encoding="utf-8") as file_out:
        for line in reference_list:
            file_out.write(line)

    # Call the original find_and_download method
    find_and_download_songs(reference_filename)

    # Clean up the extra list that was generated
    if os.path.exists(reference_filename):
        os.remove(reference_filename)


# This is prompt to handle the multicore queries
# An effort has been made to create an easily automated interface
# Autoeneable: bool allows for no prompts and defaults to max core usage
# Maxcores: int allows for automation of set number of cores to be used
# Buffercores: int allows for an allocation of unused cores (default 1)
def enable_multicore(autoenable=False, maxcores=None, buffercores=1):
    native_cpu_count = multiprocessing.cpu_count() - buffercores
    if autoenable:
        if maxcores:
            if maxcores <= native_cpu_count:
                return maxcores
            else:
                print("Too many cores requested, single core operation fallback")
                return 1
        return multiprocessing.cpu_count() - 1
    # multicore_query = input("Enable multiprocessing (Y or N): ")
    multicore_query = "Y"
    if multicore_query not in ["Y", "y", "Yes", "YES", "YEs", "yes"]:
        return 1
    # core_count_query = int(input("Max core count (0 for allcores): "))
    core_count_query = 0
    if core_count_query == 0:
        return native_cpu_count
    if core_count_query <= native_cpu_count:
        return core_count_query
    else:
        print("Too many cores requested, single core operation fallback")
        return 1

def process_downloads_spotify(path, url):
    print("Please read README.md for use instructions.")
    data_path = path
    uri = url
    data_path = os.path.join(data_path, "mp3","spotify")
    generate_path(data_path)
    os.chdir(data_path)
    multicore_support = enable_multicore(autoenable=False, maxcores=None, buffercores=1)
    if uri.split("/")[-2] == "track":
        playlist_name = write_track(uri)
    elif uri.split("/")[-2] == "album":
        playlist_name = write_album(uri)
    elif uri.split("/")[-2] == "playlist":
        playlist_name = write_playlist(uri)
    reference_file = "{}.txt".format(playlist_name)
    # Create the playlist folder
    generate_path("data")
    os.chdir("data")
    print(os.getcwd())
    # Enable multicore support
    if multicore_support > 1:
        multicore_find_and_download_songs(reference_file, multicore_support)
    else:
        find_and_download_songs(reference_file)
    os.remove(f"{reference_file}")
    print("Operation complete.")
# if __name__ == "__main__":
#     # Parameters
#     print("Please read README.md for use instructions.")
#     data_path = input("Data Path: ")
#     uri = input("Playlist URI/Link: ")
#     data_path = os.path.join(data_path, "mp3","spotify")
#     generate_path(data_path)
#     os.chdir(data_path)
#     multicore_support = enable_multicore(autoenable=False, maxcores=None, buffercores=1)
#     if uri.split("/")[-2] == "track":
#         playlist_name = write_track(uri)
#     elif uri.split("/")[-2] == "album":
#         playlist_name = write_album(uri)
#     elif uri.split("/")[-2] == "playlist":
#         playlist_name = write_playlist(uri)
#     reference_file = "{}.txt".format(playlist_name)
#     # Create the playlist folder
#     generate_path("data")
#     os.chdir("data")
#     print(os.getcwd())
#     # Enable multicore support
#     if multicore_support > 1:
#         multicore_find_and_download_songs(reference_file, multicore_support)
#     else:
#         find_and_download_songs(reference_file)
#     os.remove(f"{reference_file}")
#     print("Operation complete.")
