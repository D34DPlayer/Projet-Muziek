import os
from pathlib import Path

import music_tag
import pytest

from . import SongDownloader


def test_downloader():
    # DOWNLOADER START
    downloader = SongDownloader({"download_dir": "./test_songs"})

    assert os.path.isdir("./test_songs") is True

    # DONWLOAD WITHOUT FETCH

    with pytest.raises(ValueError):
        downloader.download_song({})

    # GET ITEM WITHOUT FETCH

    assert downloader["title"] is None

    # SONG FETCH
    right_url = "https://www.youtube.com/watch?v=f1N5lZw7e78"
    fake_url = "https://www.youtube.com/watch?v=dQw4w9W"

    assert downloader.fetch_song(fake_url) is None
    video_info = downloader.fetch_song(right_url)
    assert video_info is not None
    assert video_info["title"] == "Slow Clap - Meme"

    # GET ITEM

    assert video_info["title"] == downloader["title"]

    # SONG DOWNLOAD
    song_data = {
        "song_name": "NAME",
        "group_name": "GROUP",
        "song_id": 69,
        "genre": "GENRE"
    }
    song_path = f"./test_songs/{song_data['song_id']}/{song_data['song_name']} - {song_data['group_name']}.mp3"
    assert os.path.exists(song_path) is False

    downloader.download_song(song_data)

    assert os.path.exists(song_path) is True

    # TAGS

    f = music_tag.load_file(song_path)

    assert f["artist"].first == song_data["group_name"]
    assert f["genre"].first == song_data["genre"]
    assert f["tracktitle"].first == song_data["song_name"]

    # TAG UPDATE

    downloader.update_metadata({**song_data, "genre": "GENRE2"})

    f = music_tag.load_file(song_path)

    assert f["artist"].first == song_data["group_name"]
    assert f["genre"].first == "GENRE2"
    assert f["tracktitle"].first == song_data["song_name"]

    # IS DOWNLOADED

    assert downloader.is_downloaded(song_data["song_id"]) is True
    assert downloader.is_downloaded(song_data["song_id"] + 2) is False

    # GET SONG PATH

    assert Path(downloader.get_song_path(song_data["song_id"])) == Path(song_path)
    assert downloader.get_song_path(song_data["song_id"] + 2) is None

    # SONG DELETE

    downloader.delete_song(song_data["song_id"])

    assert os.path.exists(song_path) is False
    assert downloader.is_downloaded(song_data["song_id"]) is False


def test_downloader_cleanup():
    for folder in os.listdir("./test_songs"):
        for file in os.listdir(f"./test_songs/{folder}"):
            os.remove(f"./test_songs/{folder}/{file}")
        os.rmdir(f"./test_songs/{folder}")
    os.rmdir("./test_songs")
