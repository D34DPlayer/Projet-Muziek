import os

from . import DBMuziek

# import pytest


def test_database():
    # DATABASE START
    db = DBMuziek("./temp.db")
    db.connect()

    assert db.connection is not None

    # TABLE VALIDATION
    assert db.validate_tables() is False

    assert db.validate_tables() is True

    # COUNT SONGS EMPTY
    assert db.count_songs() == 0

    # SETTINGS
    assert db.get_setting("test") is None
    db.set_setting("test", "value")
    db.commit()
    assert db.get_setting("test") == "value"

    # CREATE GROUP AND GET GROUP(S)
    group_data = {
        "name": "TestGroup",
        "members": ["Member1", "Member2"]
    }

    group_data["id"] = db.create_group(**group_data)
    db.commit()
    group_data_bis = db.get_group(group_data["name"])
    group_data_verbose = db.get_group(group_data["name"].upper(), True)
    groups = db.get_groups()

    assert group_data_bis["group_name"] == group_data["name"]
    assert group_data_bis["members"] == ",".join(group_data["members"])
    assert group_data_bis["group_id"] == group_data["id"]

    assert group_data_verbose[0]["group_name"] == group_data["name"]

    assert group_data_verbose[1] == 0
    assert group_data_verbose[2] == 0

    assert db.get_group("FakeGroup") is None

    assert len(groups) == 1
    assert groups[0]["group_name"] == group_data["name"]

    # UPDATE GROUP
    db.update_group(group_data["id"], group_data["members"][:1])
    db.commit()
    assert db.get_group(group_data["name"])["members"] == group_data["members"][0]

    # CREATE SONG AND GET SONG
    featuring_id = db.create_group("FeatGroup", ["Member3"])
    db.commit()

    song_data = {
        "name": "TestSong",
        "link": "test.link",
        "genre": "Genre",
        "duration": 69,
        "group_id": group_data["id"],
        "featuring": [featuring_id]
    }

    song_data["id"] = db.create_song(**song_data)
    db.commit()
    song_data_bis = db.get_song(song_data["name"], group_data["id"])
    song_data_upper = db.get_song(song_data["name"].upper())

    assert song_data_bis["song_id"] == song_data["id"]
    assert song_data_bis["song_name"] == song_data["name"]
    assert song_data_bis["duration"] == song_data["duration"]
    assert song_data_bis["group_name"] == group_data["name"]
    assert song_data_bis["link"] == song_data["link"]
    assert song_data_bis["genre"] == song_data["genre"]

    assert len(song_data_upper) == 1
    assert song_data_upper[0]["song_name"] == song_data["name"]

    assert len(db.get_song("FakeSong")) == 0

    # GET SONG FEATURING
    featuring = db.get_song_featuring(song_data["id"])

    assert len(featuring) == 1
    assert featuring[0]["group_name"] == "FeatGroup"
    assert featuring[0]["members"] == "Member3"
    assert featuring[0]["group_id"] == featuring_id

    # UPDATE SONG
    db.update_song(song_data["id"], song_data["link"], "OtherGenre", 420, song_data["featuring"])
    db.commit()
    song_data_bis = db.get_song(song_data["name"], group_data["id"])

    assert song_data_bis["song_id"] == song_data["id"]
    assert song_data_bis["song_name"] == song_data["name"]
    assert song_data_bis["duration"] == 420
    assert song_data_bis["group_name"] == group_data["name"]
    assert song_data_bis["link"] == song_data["link"]
    assert song_data_bis["genre"] == "OtherGenre"

    # COUNT SONGS
    assert db.count_songs() == 1
    assert db.count_songs({"genre": "OtherGenRE"}) == 1
    assert db.count_songs({"name": "TestSonG"}) == 1
    assert db.count_songs({"group": "TestGrouP"}) == 1
    assert db.count_songs({"genre": "GenreX"}) == 0
    assert db.count_songs({"genre": "OTherGenRE", "group": "tGro"}) == 1
    assert db.count_songs({"genre": "otherGenRE", "name": "songg"}) == 0

    # GET SONGS
    assert len(db.get_songs()) == 1
    assert db.get_songs()[0]["song_name"] == song_data["name"]
    assert len(db.get_songs({"genre": "OtherGenRE"})) == 1
    assert len(db.get_songs({"name": "TestSonG"})) == 1
    assert len(db.get_songs({"group": "TestGrouP"})) == 1
    assert len(db.get_songs({"genre": "OtherGenREX"})) == 0
    assert len(db.get_songs({"genre": "OthErGenRE", "group": "tGro"})) == 1
    assert len(db.get_songs({"genre": "OtherGEnRE", "name": "songg"})) == 0

    # CREATE ALBUM AND GET ALBUM(S)
    album_data = {
        "name": "TestAlbum",
        "songs": [song_data["id"]],
        "group_id": group_data["id"]
    }

    album_data["id"] = db.create_album(**album_data)
    db.commit()
    album_data_bis = db.get_album(album_data["name"], album_data["group_id"])
    album_data_upper = db.get_album(album_data["name"].upper())
    albums = db.get_albums()

    assert album_data_bis["album_name"] == album_data["name"]
    assert album_data_bis["album_id"] == album_data["id"]
    assert album_data_bis["group_id"] == album_data["group_id"]
    assert album_data_bis["group_name"] == group_data["name"]

    assert len(album_data_upper) == 1
    assert album_data_upper[0]["album_name"] == album_data["name"]

    assert len(albums) == 1
    assert albums[0]["album_name"] == album_data["name"]

    # GET ALBUM SONGS
    album_songs = db.get_album_songs(album_data["id"])

    assert len(album_songs) == 1
    assert album_songs[0]["song_id"] == song_data["id"]
    assert album_songs[0]["song_name"] == song_data["name"]
    assert album_songs[0]["duration"] == 420
    assert album_songs[0]["group_name"] == group_data["name"]
    assert album_songs[0]["link"] == song_data["link"]
    assert album_songs[0]["genre"] == "OtherGenre"

    # UPDATE ALBUM
    other_song_data = {
        "name": "TestSong2",
        "link": "test.link.2",
        "genre": "Genre",
        "duration": 69,
        "group_id": group_data["id"],
        "featuring": []
    }

    other_song_id = db.create_song(**other_song_data)

    db.update_album(album_data["id"], [song_data["id"], other_song_id])

    other_album_songs = db.get_album_songs(album_data["id"])

    assert len(other_album_songs) == 2
    assert other_album_songs[0]["duration"] == 420
    assert other_album_songs[1]["duration"] == 69

    # CREATE PLAYLIST AND GET PLAYLIST(S)
    playlist_data = {
        "name": "TestPlaylist",
        "author": "Joe"
    }

    assert len(db.get_playlists()) == 0
    playlist_data["id"] = db.create_playlist(**playlist_data)
    db.commit()
    playlists = db.get_playlists()
    playlist = db.get_playlist(playlist_data["name"].upper())

    assert len(playlists) == 1
    assert playlists[0]["playlist_name"] == playlist_data["name"]

    assert playlist["playlist_name"] == playlist_data["name"]
    assert playlist["author"] == playlist_data["author"]
    assert playlist["playlist_id"] == playlist_data["id"]

    # ADD SONG PLAYLIST AND GET PLAYLIST SONGS
    db.add_song_playlist(playlist_data["id"], song_data['id'])
    db.add_song_playlist(playlist_data["id"], other_song_id)
    db.commit()
    playlist_songs = db.get_playlist_songs(playlist_data["id"])

    assert playlist_songs[0]["song_id"] == song_data["id"]
    assert playlist_songs[0]["song_name"] == song_data["name"]
    assert playlist_songs[0]["link"] == song_data["link"]
    assert playlist_songs[0]["genre"] == "OtherGenre"

    assert playlist_songs[1]["song_id"] == other_song_id

    # GET GENRES
    assert db.get_genres() == ['Othergenre', 'Genre']

    # DATABASE END
    db.disconnect()

    assert db.connection is None

    # DB CONTEXT MANAGER
    with db:
        assert db.connection is not None
        db.get_song(song_data["name"])

    assert db.connection is None


def test_database_cleanup():
    os.remove("./temp.db")
