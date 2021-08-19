from config import login, password
from yandex_music import Client

client = Client.from_credentials(login, password)

for track in client.users_likes_tracks():
    title = ""
    for artist in track.fetch_track().artists:
        title += artist.name + " "
    title += track.fetch_track().title + ".mp3"

    print(track.fetch_track().download(title, bitrate_in_kbps=320))
