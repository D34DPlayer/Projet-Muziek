from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from ..downloader import SongDownloader
from ..database import DBMuziek


class DetailsPlaylist(BoxLayout):
    def __init__(self, db: DBMuziek, playlist_id: int, back_action=None, **kwargs):
        super(DetailsPlaylist, self).__init__(**kwargs)
        self._db = db
        self.playlist_id = playlist_id

        self.playlist = None
        self.songs = None

        self.update_data(self.playlist_id)

        if back_action:
            btn = Button(text="Go back")
            btn.bind(on_release=lambda _: back_action())
            self.add_widget(btn)

    def update_data(self, playlist_id):
        playlist = self._db.get_playlist(playlist_id=playlist_id)

        if playlist:
            self.playlist = playlist
            self.playlist_id = playlist_id
            self.ids.playlist_name.text = playlist["playlist_name"]

            self.songs = self._db.get_playlist_songs(playlist_id)
            self.ids.song_list.clear_widgets()
            self.ids.song_list_container.size_hint = (1, len(self.songs))

            for song in self.songs:
                label = Label(text=song["song_name"])
                self.ids.song_list.add_widget(label)

            self.ids.dl_button.disabled = False

    def download_playlist(self):
        dl = SongDownloader()

        for song in self.songs:
            if dl.is_downloaded(song["song_id"]):
                dl.delete_song(song["song_id"])

            if not(dl.fetch_song(song["link"])):
                return

            dl.download_song(song)
