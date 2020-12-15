from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.lang.builder import Builder

from ..database import DBMuziek
from .popup_group import PopupGroup
from .popup_album import PopupAlbum
from .popup_song import PopupSong

Builder.load_file("libs/graphical_interface/details_group.kv")


class DetailsGroup(BoxLayout):
    def __init__(self, db: DBMuziek, group_id: int, back_action=None, **kwargs):
        super(DetailsGroup, self).__init__(**kwargs)
        self._db = db
        self.group_id = group_id

        self.group = None

        self.update_data(self.group_id)

        if back_action:
            btn = Button(text="Go back")
            btn.bind(on_release=lambda _: back_action())
            self.add_widget(btn)

    def edit_group(self):
        if self.group:
            edit = PopupGroup(self._db, self.group)
            edit.bind(on_dismiss=lambda _: self.update_data(self.group_id))
            edit.open()

    def update_data(self, group_id):
        group_query = self._db.get_group(group_id=group_id, verbose=True)

        if group_query:
            self.group = group_query[0]
            self.group_id = group_id
            self.ids.group_name.text = self.group["group_name"]
            self.ids.members.text = ", ".join(self.group["members"].split(","))
            self.ids.songs.text = str(group_query[1])
            self.ids.albums.text = str(group_query[2])

            self.ids.edit_button.disabled = False
            self.ids.add_song_button.disabled = False
            self.ids.add_album_button.disabled = False

    def add_song(self):
        if self.group:
            data = {"group_id": self.group_id, "group_name": self.group["group_name"]}

            edit = PopupSong(self._db, data)
            edit.bind(on_dismiss=lambda _: self.update_data(self.group_id))
            edit.open()

    def add_album(self):
        if self.group:
            data = {"group_id": self.group_id, "group_name": self.group["group_name"]}

            edit = PopupAlbum(self._db, data)
            edit.bind(on_dismiss=lambda _: self.update_data(self.group_id))
            edit.open()
