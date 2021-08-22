import eyed3


def save_mp3(file_path, artist, album, title, track_num):
    audio_file = eyed3.load(file_path)
    audio_file.initTag()
    audio_file.tag.artist = artist
    audio_file.tag.album = album
    audio_file.tag.title = title
    audio_file.tag.track_num = track_num
    audio_file.tag.save()
