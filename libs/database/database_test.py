from . import DBMuziek
import os
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

    # CREATE GROUP AND GET GROUP
    group_data = {
        "name": "TestGroup",
        "members": ["Member1", "Member2"]
    }

    group_data["id"] = db.create_group(**group_data)
    db.commit()
    group_data_bis = db.get_group(group_data["name"])
    group_data_verbose = db.get_group(group_data["name"].upper(), True)

    assert group_data_bis["group_name"] == group_data["name"]
    assert group_data_bis["members"] == ",".join(group_data["members"])
    assert group_data_bis["group_id"] == group_data["id"]

    assert group_data_verbose[0]["group_name"] == group_data["name"]

    assert group_data_verbose[1] == 0
    assert group_data_verbose[2] == 0

    assert db.get_group("FakeGroup") is None

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
        "duration": 69
    }

    song_data["id"] = db.create_song(**song_data, group_id=group_data["id"], featuring=[featuring_id])
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

    # UPDATE SONG
    db.update_song(song_data["id"], song_data["link"], "OtherGenre", 420, [featuring_id])
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

    # TODO: CREATE ALBUM AND GET ALBUM

    # TODO: UPDATE ALBUM

    # TODO: CREATE PLAYLIST AND GET PLAYLIST

    # TODO: ADD SONG PLAYLIST

    # TODO: GET PLAYLIST SONGS

    # DATABASE END
    db.disconnect()

    os.remove("./temp.db")
