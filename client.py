import os

from config import login, password
from yandex_music import Client
from work_with_mp3 import save_mp3

client = Client.from_credentials(login, password)

for playlist in client.users_playlists_list():
    if playlist.title == "Filatov & Karas":
        playlist_path = "./" + playlist.title + "/"
        os.makedirs(playlist_path, exist_ok=True)
        for track in client.users_playlists(playlist.kind).tracks:
            track_title = track.fetch_track().title if track.fetch_track().version is None \
                else track.fetch_track().title + " (" + track.fetch_track().version + ")"
            artists = ""
            for artist in track.fetch_track().artists:
                if artist != track.fetch_track().artists[len(track.fetch_track().artists) - 1]:
                    artists += artist.name + ","
                else:
                    artists += artist.name
            file_path = playlist_path + artists + " - " + track_title + ".mp3"
            track.fetch_track().download(file_path, bitrate_in_kbps=320)
            save_mp3(file_path,
                     artists,
                     track.fetch_track().albums[0].title,
                     track_title,
                     track.fetch_track().albums[0].track_position["index"])
