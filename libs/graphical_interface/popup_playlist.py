from kivy.uix.popup import Popup
from kivy.lang.builder import Builder

from ..database import DBMuziek
from .popup_song import GroupDropdown, PopupSong
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
