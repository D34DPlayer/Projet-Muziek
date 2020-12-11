from . import utils as u


def check_print(capsys, text):
    captured = capsys.readouterr()
    assert captured.out == text


def set_input(monkeypatch, text):
    def fake_input(x):
        print(x)
        return text
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
            "featuring": ["ton", "chien"]
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


def test_format_duration():
    assert u.format_duration(59) == "0:59"
    assert u.format_duration(326) == "5:26"
    assert u.format_duration(None) == "??:??"


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


def test_encoding():
    data = {
        "playlist": {"author": "Paul"},
        "groups": [{"group_name": "TestGroup"}]
    }

    encoded = u.encode(data)
    decoded = u.decode(encoded)

    assert data is not decoded
    assert data == decoded
