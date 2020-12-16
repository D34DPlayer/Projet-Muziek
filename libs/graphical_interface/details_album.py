from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.lang.builder import Builder

from ..database import DBMuziek
from .popup_album import PopupAlbum

Builder.load_file("libs/graphical_interface/details_album.kv")


class DetailsAlbum(BoxLayout):
    def __init__(self, db: DBMuziek, album_id: int, back_action=None, **kwargs):
        super(DetailsAlbum, self).__init__(**kwargs)
        self._db = db
        self.album_id = album_id

        self.album = None

        self.update_data(self.album_id)

        if back_action:
            btn = Button(text="Go back")
            btn.bind(on_release=lambda _: back_action())
            self.add_widget(btn)

    def edit_album(self):
        if self.album:
            edit = PopupAlbum(self._db, self.album)
            edit.bind(on_dismiss=lambda _: self.update_data(self.album_id))
            edit.open()

    def update_data(self, album_id):
        album = self._db.get_album(album_id=album_id)

        if album:
            self.album = album
            self.album_id = album_id
            self.ids.album_name.text = album["album_name"]
            self.ids.group_name.text = album["group_name"]

            songs = self._db.get_album_songs(album_id)
            self.ids.song_list.clear_widgets()
            self.ids.song_list_container.size_hint = (1, len(songs))

            for song in songs:
                label = Label(text=song["song_name"])
                self.ids.song_list.add_widget(label)

            self.ids.edit_button.disabled = False
