from itertools import product
from multiprocessing import Manager, Pool
import os
import time

from config import music_dir_path, token
from work_with_mp3 import save_mp3
from yandex_music import Client


def split_list(arr, size):
    result_arr = []
    while len(arr) > size:
        piece = arr[:size]
        result_arr.append(piece)
        arr = arr[size:]
    result_arr.append(arr)
    return result_arr


def dowload_track(playlist_title, track):
    print("Start")
    clock_track = time.time()
    playlist_path = music_dir_path + playlist_title + "/"
    os.makedirs(playlist_path, exist_ok=True)
    full_track = track.fetch_track()

    track_title = full_track.title if full_track.version is None else full_track.title + " (" + full_track.version + ")"
    artists = ", ".join([artist.name for artist in full_track.artists])
    for replace in [(r"/", "_"), ('"', ""), ("?", ""), (">", "("), ("<", ")"), (":", " ")]:
        track_title = track_title.replace(*replace)

    file_path = "{}{} - {}.mp3".format(playlist_path,
                                       artists.replace(r"/", "_"),
                                       track_title)
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
    avg_time = time.time() - clock_track

    print("Finish ", avg_time)
    return True if success is None else False


def tracks_loop(tracks):
    for item in tracks[0]:
        with tracks[3]:
            tracks[1].value += 1
        print(
            f"Track {tracks[1].value}/{tracks[2].value}"
            f" {round(((tracks[1].value / tracks[2].value) * 100), 2)} % download {dowload_track(*item)}")


errors = []

if __name__ == '__main__':
    # client = Client.from_credentials(login, password, captcha_callback=proc_captcha)
    # print(client.token)
    client = Client.from_token(token, report_new_fields=False)
    client.accountSettingsSet(timeout=300)
    clock = time.time()
    tracks = []
    for playlist in client.users_playlists_list():
        playlist_title = playlist.title.replace(r"/", "_")
        for track in client.users_playlists(playlist.kind).tracks:
            tracks.append((playlist_title, track))

    with Manager() as manager:
        lock = manager.Lock()
        n = manager.Value(int, 0)
        len_tracks = manager.Value(int, len(tracks))

        with Pool() as pool:
            cpu_count = os.cpu_count()
            subcount = len_tracks.value // cpu_count
            if len_tracks.value % cpu_count:
                subcount += 1
            slice_size = subcount
            
            data = product(split_list(tracks, int(slice_size)), [n], [len_tracks], [lock])
            pool.map(tracks_loop, data)

    print("All time: ", (time.time() - clock) / 60.0)
    for error in errors:
        print(error)
