import math

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from typing import List
from ..database import DBMuziek, format_duration

Builder.load_file('libs/graphical_interface/main_window.kv')


class PageLayout(BoxLayout):
    def __init__(self, header: List[str], sizes: List[int], total_items: int, **kwargs):
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

        self.page = 1

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
            row = BoxLayout(orientation='horizontal', size_hint_y=None, height=25)
            for width, value in zip(self.cols_size, entry):
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


class GroupsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[r['group_name'], r['members']] for r in db.get_groups()]
        super().__init__(['Group Name', 'Members'], [.4, .6], len(self.content), **kwargs)


class SongsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        count = db.count_songs()
        super().__init__(['Author', 'Title', 'Duration'], [.4, .4, .2], count, **kwargs)

    def get_page(self, page: int) -> List[List[str]]:
        songs = self._db.get_songs(offset=page * self.per_page, limit=self.per_page)
        return [[s['group_name'], s['song_name'], format_duration(s['duration'])] for s in songs]


class AlbumsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[a['group_name'], a['album_name']] for a in db.get_albums()]
        super().__init__(['Author', 'Title'], [.5, .5], len(self.content), **kwargs)


class PlaylistsWidget(PageLayout):
    def __init__(self, db: DBMuziek, **kwargs):
        self._db = db
        self.content = [[a['author'], a['playlist_name']] for a in db.get_playlists()]
        super().__init__(['Author', 'Name'], [.5, .5], len(self.content), **kwargs)


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
