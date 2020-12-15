from kivy.lang.builder import Builder
from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown

from ..database import DBMuziek
from .popup_song import GroupDropdown, PopupSong
from .utils import ErrorPopup

Builder.load_file("libs/graphical_interface/popup_album.kv")


class PopupAlbum(Popup):
    def __init__(self, db: DBMuziek, update_data=None, **kwargs):
        super(PopupAlbum, self).__init__(**kwargs)
        self._db = db
        self.group_data = None
        self._update_id = None

        self.ids["group_input"] = GroupDropdown(self._db)
        self.ids.group_container.add_widget(self.ids["group_input"])

        self.ids["group_input"].dropdown.bind(on_select=lambda _, btn: self.group_select(btn))

        self.add_song_field()
        self.title = "Create an album"

        if update_data:
            self.update_data(update_data)

    def add_song_field(self):
        song_list = self.ids.song_list

        song_input = GroupSongDropdown(self._db, self.group_data)
        song_list.add_widget(song_input, 1)

        song_list.counter += 1

        self.ids[f"song{song_list.counter}"] = song_input
        self.ids.song_list_container.size_hint = (1, song_list.counter + 1)

    def group_select(self, btn):
        g_id = btn.group_id if btn else None
        g_name = btn.text if btn else None

        self.group_data = {"group_id": g_id, "group_name": g_name}

        for i in range(1, self.ids.song_list.counter + 1):
            self.ids[f"song{i}"].update_songs(g_id, g_name)

    def update_data(self, data):
        data = dict(data)
        if "group_id" in data:
            self.ids.group_input.update_data(data)
            self.group_select(self.ids.group_input)
            self.ids.group_input.disabled = True
        if "album_id" in data:
            self._update_id = data["album_id"]

            song_list = self.ids.song_list
            songs = self._db.get_album_songs(self._update_id)
            self.title = "Modify an album"

            for i, song in enumerate(songs, 1):
                if i > song_list.counter:
                    self.add_song_field()

                self.ids[f"song{i}"].update_data(song)

        if "album_name" in data:
            self.ids.name_input.text = data["album_name"]
            self.ids.name_input.disabled = True

    def validate_form(self):
        buffer = {}
        name_input = self.ids.name_input
        song_list = self.ids.song_list
        group_input = self.ids.group_input

        if group_input.group_id is None:
            ErrorPopup('No group was provided.')
            return None

        buffer["group_id"] = group_input.group_id

        if not name_input.text:
            ErrorPopup("No name provided.")
            return None
        elif not self._update_id and self._db.get_album(name_input.text):
            ErrorPopup("The album already exists.")
            return None

        buffer["name"] = name_input.text

        songs = [self.ids[f"song{i + 1}"].song_id
                 for i in range(song_list.counter)
                 if self.ids[f"song{i + 1}"].song_id]

        if not songs:
            ErrorPopup("No songs provided.")
            return None

        buffer["songs"] = list(set(songs))

        return buffer

    def submit_form(self):
        data = self.validate_form()
        if data:
            with self._db.connection:
                if self._update_id:
                    self._db.update_album(self._update_id, data["songs"])
                else:
                    self._db.create_album(**data)
            self.dismiss()


class GroupSongDropdown(Button):
    def __init__(self, db: DBMuziek, default=None, **kwargs):
        super(GroupSongDropdown, self).__init__(**kwargs)

        self.dropdown = DropDown()

        self.song_id = None
        self.text = "<Choice>"

        self._db = db
        self.songs = None
        self.g_id = None
        self.g_name = None
        self.disable()

        self.update_data(default)

        self.bind(on_release=self.open)
        self.dropdown.bind(on_select=lambda _, btn: self.on_select(btn))

    def disable(self):
        self.disabled = True

    def enable(self):
        self.disabled = False

    def update_data(self, data):
        if data and "group_id" in data:
            self.g_id = data["group_id"]
            self.g_name = data["group_name"]
            if "song_id" in data:
                self.song_id = data["song_id"]
                self.text = data["song_name"]
            if self.g_id is not None:
                self.update_songs()
                self.enable()

    def reset_choice(self, dd):
        if dd:
            dd.dismiss()
        self.text = "<Choice>"
        self.song_id = None

    def update_songs(self, g_id=-1, g_name=None):
        if g_id is None:
            self.reset_choice(None)
            self.g_id = None
            self.disable()
            return
        elif g_id != -1 and self.g_id != g_id:
            self.g_id = g_id
            self.enable()
            self.reset_choice(None)
        if g_name:
            self.g_name = g_name

        self.songs = self._db.get_songs({"group_id": self.g_id})

        self.dropdown.clear_widgets()

        btn = Button(text="<Choice>", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: self.reset_choice(self.dropdown))
        self.dropdown.add_widget(btn)

        for song in self.songs:
            btn = SongButton(text=song["song_name"], size_hint_y=None, height=44)
            btn.set_id(song["song_id"])
            btn.bind(on_release=self.dropdown.select)

            self.dropdown.add_widget(btn)

        btn = Button(text="+", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: summon_popup_song(self._db, self.dropdown, self.g_id, self.g_name))
        self.dropdown.add_widget(btn)

    def open(self, btn):
        self.update_songs()
        self.dropdown.open(btn)

    def on_select(self, btn):
        self.text = btn.text
        self.song_id = btn.song_id


class SongButton(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

        self.song_id = None

    def set_id(self, i):
        self.song_id = i


def summon_popup_song(db: DBMuziek, dd: DropDown, g_id=None, g_name=None):
    dd.dismiss()
    data = {"group_id": g_id, "group_name": g_name}
    PopupSong(db, update_data=data).open()
