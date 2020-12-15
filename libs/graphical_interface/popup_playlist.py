from kivy.uix.popup import Popup
from kivy.uix.button import Button
from kivy.uix.dropdown import DropDown
from kivy.lang.builder import Builder

from ..database import DBMuziek
from .utils import ErrorPopup
from ..console_interface import create_playlist

Builder.load_file("libs/graphical_interface/popup_playlist.kv")


class PopupPlaylist(Popup):
    def __init__(self, db: DBMuziek):
        super(PopupPlaylist, self).__init__()
        self._db = db

    def submit_form(self):
        name = self.ids.name_input.text

        if self._db.get_playlist(name):
            ErrorPopup("That playlist already exists.")
        else:
            with self._db.connection:
                create_playlist(self._db, name)
            self.dismiss()


class PopupAddToPlaylist(Popup):
    def __init__(self, db: DBMuziek, song_id: int):
        super(PopupAddToPlaylist, self).__init__()
        self._db = db
        self.song_id = song_id

        self.ids["playlist_input"] = PlaylistDropdown(self._db)
        self.ids.playlist_container.add_widget(self.ids["playlist_input"])

    def submit_form(self):
        playlist_id = self.ids.playlist_input.playlist_id

        if not self._db.get_playlist(playlist_id=playlist_id):
            ErrorPopup("That playlist doesn't exist.")
        elif not self._db.get_song(song_id=self.song_id):
            ErrorPopup("The song doesn't exist.")
        else:
            with self._db.connection:
                self._db.add_song_playlist(playlist_id, self.song_id)
        self.dismiss()


class PlaylistDropdown(Button):
    def __init__(self, db: DBMuziek,**kwargs):
        super(PlaylistDropdown, self).__init__(**kwargs)
        self._db = db

        self.dropdown = DropDown()

        self.playlist_id = None
        self.text = "<Choice>"

        self.playlists = None
        self.update_playlists()

        self.bind(on_release=self.open)
        self.dropdown.bind(on_select=lambda _, btn: self.on_select(btn))

    def reset_choice(self, dd=None):
        if dd:
            dd.dismiss()
        self.text = "<Choice>"
        self.playlist_id = None

    def update_playlists(self):
        self.playlists = self._db.get_playlists()
        self.dropdown.clear_widgets()

        btn = Button(text="<Choice>", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: self.reset_select())
        self.dropdown.add_widget(btn)

        for playlist in self.playlists:
            btn = PlaylistButton(text=playlist["playlist_name"], size_hint_y=None, height=44)
            btn.set_id(playlist["playlist_id"])
            btn.bind(on_release=self.dropdown.select)

            self.dropdown.add_widget(btn)

        btn = Button(text="+", size_hint_y=None, height=44)
        btn.bind(on_release=lambda _: summon_popup_playlist(self._db, self.dropdown))
        self.dropdown.add_widget(btn)

    def reset_select(self):
        self.reset_choice()
        self.dropdown.select(None)

    def open(self, btn):
        self.update_playlists()
        self.dropdown.open(btn)

    def on_select(self, btn=None):
        if btn is not None:
            self.text = btn.text
            self.playlist_id = btn.playlist_id


class PlaylistButton(Button):
    def __init__(self, **kwargs):
        super(Button, self).__init__(**kwargs)

        self.playlist_id = None

    def set_id(self, i):
        self.playlist_id = i


def summon_popup_playlist(db: DBMuziek, dd: DropDown):
    dd.dismiss()
    PopupPlaylist(db).open()
