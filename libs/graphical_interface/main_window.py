from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from typing import List
from ..database import DBMuziek, format_duration

Builder.load_file('libs/graphical_interface/main_window.kv')


class Root(BoxLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        super().__init__(**kwargs)
        self._db = db

    def display_groups(self):
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(GroupsWidget(self._db))

    def display_songs(self):
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(SongsWidget(self._db))

    def display_albums(self):
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(AlbumsWidget(self._db))

    def display_playlists(self):
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(PlaylistsWidget(self._db))


class MainWindow(App):
    def __init__(self, db: DBMuziek, **kwargs):
        super().__init__(**kwargs)
        self._db = db
        self.root = None

    def build(self):
        self.root = Root(self._db)
        return self.root
