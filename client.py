from config import login, password
from yandex_music import Client

client = Client.from_credentials(login, password)

for playlist in client.users_playlists_list():
    if playlist.title == "Aris":
        title = "./" + playlist.title + "/"

        for track in client.users_playlists(playlist.kind).tracks:

            for artist in track.fetch_track().artists:
                title += artist.name + " "
            title += track.fetch_track().title + ".mp3"

            track.fetch_track().download(title, bitrate_in_kbps=320)
