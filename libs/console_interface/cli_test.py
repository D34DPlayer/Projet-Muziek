import os

from ..database import DBMuziek
from . import add_group
from . import utils as u


def check_print(capsys, text):
    captured = capsys.readouterr()
    assert captured.out == text


def set_input(monkeypatch, text):
    if not isinstance(text, list):
        text = [text]

    text_gen = (s for s in text)

    def fake_input(x):
        print(x)
        return next(text_gen, None)

    monkeypatch.setattr('builtins.input', fake_input)


# TEST UTILS
def test_print_underline(capsys):
    u.print_underline("test", style="=")
    check_print(capsys, "test\n====\n")

    u.print_underline("test", "alt", style="=")
    check_print(capsys, "test alt\n========\n")

    u.print_underline("Test")
    check_print(capsys, "Test\n----\n")

    u.print_underline("Abc", "cdb", sep=",", style="=")
    check_print(capsys, "Abc,cdb\n=======\n")


def test_display_songs(capsys):
    songs = [
        {
            "song_name": "TestSong",
            "duration": 90,
            "group_name": "TestGroup",
            "featuring": [{"group_name": "ton"}, {"group_name": "chien"}]
        },
        {
            "song_name": "TestSong",
            "song_id": 3,
            "duration": 30,
            "group_name": "TestGroup2",
            "featuring": []
        }
    ]

    u.display_songs([])
    check_print(capsys, "<empty>\n")

    u.display_songs(songs[1:])
    check_print(capsys, "3. TestSong (0:30) - TestGroup2\n")

    u.display_songs(songs)
    check_print(capsys, "1. TestSong (1:30) - TestGroup (ft. ton, chien)\n3. TestSong (0:30) - TestGroup2\n")


def test_question(monkeypatch, capsys):
    set_input(monkeypatch, "")
    assert u.question("Test", "default") == "default"
    check_print(capsys, "Test [default]:\n")

    set_input(monkeypatch, "ID")
    assert u.question("TeSt") == "ID"
    check_print(capsys, "TeSt:\n")


def test_question_choice(monkeypatch, capsys):
    assert u.question_choice("Oy", []) is None

    set_input(monkeypatch, "y")
    assert u.question_choice("TeSt", ["y", "n"]) == "y"
    check_print(capsys, "TeSt [y/n]:\n")


def test_pagination(monkeypatch, capsys):
    set_input(monkeypatch, '4')
    assert u.pagination(20, 8) == 4
    check_print(capsys, "Pages: 1 2 3 .. 6 7 [8] 9 10 .. 18 19 20\nDisplay another page: \n")

    set_input(monkeypatch, '3')
    assert u.pagination(22, 22) == 3
    check_print(capsys, "Pages: 1 2 3 .. 20 21 [22]\nDisplay another page: \n")


def test_choose(monkeypatch, capsys):
    query = [{
        "group_name": "Joe"
    }, {
        "group_name": "Mama"
    }]

    set_input(monkeypatch, '2')
    assert u.choose_song(query) is query[1]
    check_print(capsys, "2 songs were found with that name from the groups:\n 1 : Joe\n 2 : Mama\nChoose one [1/2]:\n")

    set_input(monkeypatch, '1')
    assert u.choose_album(query) is query[0]
    check_print(capsys, "2 albums were found with that name from the groups:\n 1 : Joe\n 2 : Mama\nChoose one [1/2]:\n")

    assert u.choose_album(query[0]) is query[0]
    assert u.choose_album(None) is None


def test_encoding():
    data = {
        "playlist": {"author": "Paul"},
        "groups": [{"group_name": "TestGroup"}]
    }

    encoded = u.encode(data)
    decoded = u.decode(encoded)

    assert data is not decoded
    assert data == decoded


def test_strip_brackets():
    assert u.strip_brackets('Music title [OFFICIAL] (remastered)') == 'Music title'
    assert u.strip_brackets('Music title []()') == 'Music title'
    assert u.strip_brackets('Music title {super}') == 'Music title'


def test_get_info_from_title():
    assert u.get_info_from_title('Author - Title [OFFICIAL] (remastered)') == ("Author", "Title")
    assert u.get_info_from_title('Title [OFFICIAL] (remastered)') == ("Unknown", "Title")
    assert u.get_info_from_title('Author- Title [OFFICIAL] - LOL') == ("Author", "Title")


# TEST CLI
def test_add_group(monkeypatch):
    with DBMuziek("cli-test.db") as db:
        group_data = {
            "group_name": "TestGroup",
            "members": ["alt", "bis"]
        }

        text = [group_data["group_name"],
                *group_data["members"],
                "Done"
                ]
        set_input(monkeypatch, text)
        add_group(db)

        group_data_bis = db.get_group(group_data["group_name"])

        assert group_data_bis["members"] == ",".join(group_data["members"])
        assert group_data_bis["group_name"] == group_data["group_name"]


def test_cli_cleanup():
    os.remove("./cli-test.db")
