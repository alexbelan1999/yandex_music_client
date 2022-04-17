"""
Yandex music client module.

Description: this file contains methods for work with yandex music client.
File: client.py
Author: Alexey Belan

"""
import os
import time

from config import music_dir_path, token
from work_with_mp3 import save_mp3
import yandex_music
from yandex_music import Client


def download_track(playlist_title: str, track: yandex_music.TrackShort):
    """
    Method for dowload track.

    Args:
        playlist_title (str) - playlist title
        track (yandex_music.TrackShort) - track to download

    Return:
        True if track download else False
    """

    clock_track = time.time()
    playlist_path = music_dir_path + playlist_title + "/"
    os.makedirs(playlist_path, exist_ok=True)
    full_track = track.fetch_track()

    track_title = full_track.title if full_track.version is None else f"{full_track.title} ({full_track.version})"
    artists = ", ".join([artist.name for artist in full_track.artists])
    for replace in [(r"/", "_"), ('"', ""), ("?", ""), (">", "("), ("<", ")"), (":", " ")]:
        track_title = track_title.replace(*replace)

    file_path = f"{playlist_path}{artists.replace(r'/', '_')} - {track_title}.mp3"
    available_bitrate = []
    for info in full_track.get_download_info():
        if info["codec"] == "mp3":
            available_bitrate.append(info["bitrate_in_kbps"])

    if not os.path.exists(file_path):
        try:
            print(file_path)
            success = full_track.download(file_path, bitrate_in_kbps=max(available_bitrate))
            save_mp3(file_path,
                     artists,
                     full_track.albums[0].title,
                     track_title,
                     full_track.albums[0].track_position["index"] if
                     full_track.albums[0].track_position is not None else 0)
        except Exception as e:
            errors.append(("Error: ", e.args, " ", file_path))
            success = 0
    else:
        success = None
    print(f"Track {track_title} downloaded in {round(time.time() - clock_track, 3)} seconds")
    return True if success is None else False


errors = []

if __name__ == '__main__':
    client: Client = Client(token).init()
    client.accountSettingsSet(timeout=360)

    clock = time.time()
    tracks = []
    for playlist in client.users_playlists_list():
        playlist_title = playlist.title.replace(r"/", "_")
        for track in client.users_playlists(playlist.kind).tracks:
            tracks.append((playlist_title, track))

    print(f"Make tracks completed in {round(time.time() - clock, 3)} seconds")

    for track in tracks:
        download_track(*track)

    print(f"All time: , {round((time.time() - clock) / 60.0, 3)} minutes")

    for error in errors:
        print(error)
