import os
import time
from itertools import product

from config import login, music_dir_path, password, token
from multiprocessing import Pool
from work_with_mp3 import save_mp3
from yandex_music import Client, exceptions

errors = []
n = 0


def split_list(arr, size):
    result_arr = []
    while len(arr) > size:
        piece = arr[:size]
        result_arr.append(piece)
        arr = arr[size:]
    result_arr.append(arr)
    return result_arr


def dowload_track(track, playlist_path):
    print("Start")
    clocl_track = time.time()
    track = track.fetch_track()
    track_title = track.title if track.version is None else track.title + " (" + track.version + ")"
    artists = ", ".join([artist.name for artist in track.artists])
    for replace in [(r"/", "_"), ('"', ""), ("?", ""), (">", "("), ("<", ")"), (":", " ")]:
        track_title = track_title.replace(*replace)

    file_path = "{}{} - {}.mp3".format(playlist_path,
                                       artists.replace(r"/", "_"),
                                       track_title)
    if not os.path.exists(file_path):
        try:
            success = track.download(file_path, bitrate_in_kbps=320)
            print(file_path)
            save_mp3(file_path,
                     artists,
                     track.albums[0].title,
                     track_title,
                     track.albums[0].track_position["index"] if
                     track.albums[0].track_position is not None else 0)
        except exceptions.InvalidBitrate:
            errors.append(("Error: ", exceptions.InvalidBitrate, " ", file_path))
            success = track.download(file_path, bitrate_in_kbps=192)
        except Exception as e:
            errors.append(("Error: ", e.args, " ", file_path))
            success = 0
    else:
        success = None
    avg_time = time.time() - clocl_track

    print("Finish ", avg_time)
    return True if success is None else False


def get_playlist(playlist, client):
    global n
    n += 1
    playlist_path = music_dir_path + playlist.title.replace(r"/", "_") + "/"
    os.makedirs(playlist_path, exist_ok=True)
    tracks = client.users_playlists(playlist.kind).tracks
    if len(os.listdir(playlist_path)) < len(tracks):
        m = 0
        for track in tracks:
            m += 1
            print("Playlist {}/{} track {}/{}".format(n, len(client.users_playlists_list()), m,
                                                      len(client.users_playlists(playlist.kind).tracks)))
            print("Download ", dowload_track(track, playlist_path))


def playlist_loop(playlist_list, client):
    for playlist in playlist_list:
        get_playlist(playlist, client)


def proc_captcha(captcha):
    captcha.download('captcha.png')
    return input('Число с картинки: ')


if __name__ == '__main__':
    # client = Client.from_credentials(login, password, captcha_callback=proc_captcha)
    # print(client.token)
    client = Client.from_token(token, report_new_fields=False)
    client.accountSettingsSet(timeout=300)
    clock = time.time()
    # for playlist in client.users_playlists_list():
    #     n = get_playlist(playlist, client, n)
    with Pool() as pool:
        cpu_count = os.cpu_count()
        playlists = client.users_playlists_list()[:150]
        subcount = len(playlists) // cpu_count
        if len(playlists) % cpu_count:
            subcount += 1
        slice_size = subcount
        pool.starmap(playlist_loop,
                     ((playlist, client) for playlist, client in
                      product(split_list(playlists, int(slice_size)), [client])))
        # pool.starmap(get_playlist,
        #              ((playlist, client) for playlist, client in
        #               product(playlists, [client])))

    print("All time: ", (time.time() - clock) / 60.0)
    for error in errors:
        print(error)
