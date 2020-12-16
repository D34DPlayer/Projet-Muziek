import glob
import math
import os

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.label import Label
from typing import List
from ..database import DBMuziek, format_duration
from .details_album import DetailsAlbum
from .details_group import DetailsGroup
from .details_playlist import DetailsPlaylist
from .details_song import DetailsSong


class Row(ButtonBehavior, BoxLayout):
    def __init__(self, id_: int, **kwargs):
        kwargs.setdefault('orientation', 'horizontal')
        kwargs.setdefault('size_hint_y', None)
        kwargs.setdefault('height', 25)
        super().__init__(**kwargs)
        self._id = id_

    def on_release(self):
        self.parent.parent.show_info(self._id)


class PageLayout(BoxLayout):
    def __init__(self, header: List[str], sizes: List[int], total_items: int, page: int = 1, **kwargs):
        super(PageLayout, self).__init__(**kwargs)
        self.header = header
        self.cols_size = sizes
        self.total_items = total_items

        assert len(header) == len(sizes)
        for i, value in enumerate(self.header):
            self.ids.header.add_widget(Label(
                text=value,
                size_hint_x=self.cols_size[i],
                underline=True
            ))

        self.page = page

    @property
    def root(self):
        return App.get_running_app().root

    @property
    def page(self):
        return self._page

    @page.setter
    def page(self, value):
        self._page = min(max(value, 1), self.total_pages)
        self.display()

    @property
    def per_page(self):
        if self.parent is None:
            return App.get_running_app().root.height // 25 - 3
        return self.parent.height // 25 - 3

    @property
    def total_pages(self):
        return math.ceil(self.total_items / self.per_page)

    def display(self):
        self.ids.body.clear_widgets()
        for entry in self.get_page(self.page - 1):
            row = Row(entry[0])
            for width, value in zip(self.cols_size, entry[1:]):
                row.add_widget(Label(
                    text=value,
                    size_hint_x=width,
                ))

            self.ids.body.add_widget(row)
        self.ids.page_index.text = f'{self.page}/{self.total_pages}'

    def get_page(self, page: int) -> List[List[str]]:
        if hasattr(self, 'content'):
            self.total_items = len(self.content)
            return self.content[page * self.per_page: (page + 1) * self.per_page]
        raise NotImplementedError

    def show_info(self, id_: int):
        raise NotImplementedError


class GroupsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[r['group_id'], r['group_name'], r['members']] for r in db.get_groups()]
        super().__init__(['Group Name', 'Members'], [.4, .6], len(self.content), **kwargs)

    def show_info(self, group_id: int):
        self.root.display(DetailsGroup(self._db, group_id, lambda: self.root.display_groups(self.page)))


class SongsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        count = db.count_songs()
        super().__init__(['Author', 'Title', 'Duration'], [.4, .4, .2], count, **kwargs)

    def get_page(self, page: int) -> List[List[str]]:
        songs = self._db.get_songs(offset=page * self.per_page, limit=self.per_page)
        return [[r['song_id'], r['group_name'], r['song_name'], format_duration(r['duration'])] for r in songs]

    def show_info(self, song_id: int):
        self.root.display(DetailsSong(self._db, song_id, lambda: self.root.display_songs(self.page)))


class AlbumsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[r['album_id'], r['group_name'], r['album_name']] for r in db.get_albums()]
        super().__init__(['Author', 'Title'], [.5, .5], len(self.content), **kwargs)

    def show_info(self, album_id: int):
        self.root.display(DetailsAlbum(self._db, album_id, lambda: self.root.display_albums(self.page)))


class PlaylistsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[r['playlist_id'], r['author'], r['playlist_name']] for r in db.get_playlists()]
        super().__init__(['Author', 'Name'], [.5, .5], len(self.content), **kwargs)

    def show_info(self, playlist_id: int):
        self.root.display(DetailsPlaylist(self._db, playlist_id, lambda: self.root.display_playlists(self.page)))


class Root(BoxLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        super().__init__(**kwargs)
        self._db = db

    def display(self, widget):
        self.ids.content.clear_widgets()
        self.ids.content.add_widget(widget)

    def display_groups(self, page: int = 0):
        self.display(GroupsWidget(self._db, page=page))

    def display_songs(self, page: int = 0):
        self.display(SongsWidget(self._db, page=page))

    def display_albums(self, page: int = 0):
        self.display(AlbumsWidget(self._db, page=page))

    def display_playlists(self, page: int = 0):
        self.display(PlaylistsWidget(self._db, page=page))


class MainWindow(App):
    def __init__(self, db: DBMuziek, **kwargs):
        for file in glob.glob(os.path.join(os.path.dirname(__file__), '*.kv')):
            Builder.load_file(file)

        super().__init__(**kwargs)
        self._db = db
        self.root = None

    def display(self, *args):
        self.root.display(*args)

    def build(self):
        self.root = Root(self._db)
        return self.root
