import os
import subprocess

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

from .popup_song import PopupSong
from .popup_playlist import PopupAddToPlaylist
from .utils import ErrorPopup, InfoPopup
from ..database import DBMuziek, format_duration
from ..downloader import SongDownloader


class DetailsSong(BoxLayout):
    def __init__(self, db: DBMuziek, song_id: int, back_action=None, **kwargs):
        super(DetailsSong, self).__init__(**kwargs)
        self._db = db
        self.song_id = song_id

        self.song = None
        self._feat_pos = 1

        self.update_data(self.song_id)

        if back_action:
            btn = Button(text="Go back")
            btn.bind(on_release=lambda _: back_action())
            self.add_widget(btn)
            self._feat_pos += 1

    def update_data(self, song_id):
        song = self._db.get_song(song_id=song_id)

        if song:
            self.song = song
            self.song_id = song_id
            self.ids.song_name.text = song["song_name"]
            self.ids.duration.text = format_duration(song["duration"])
            self.ids.link.text = song["link"]
            self.ids.genre.text = song["genre"]
            self.ids.group_name.text = song["group_name"]

            if 'featuring' in self.ids:
                self.remove_widget(self.ids['featuring'])

            if song["featuring"]:
                el = BoxLayout(orientation="horizontal", padding=[20, 10, 20, 10])
                el.add_widget(Label(text="Featuring:"))
                el.add_widget(Label(text=", ".join([f["group_name"] for f in song["featuring"]])))

                self.ids["featuring"] = el
                self.add_widget(el, self._feat_pos)

            self.ids.dl_button.disabled = False
            self.ids.pl_button.disabled = False
            self.ids.edit_button.disabled = False

            self.check_download()

    def download_song(self):
        dl = SongDownloader({"progress_hooks": [self.check_download]})

        if dl.is_downloaded(self.song_id):
            dl.delete_song(self.song_id)

        if not(dl.fetch_song(self.song["link"])):
            ErrorPopup("There was an error when trying to download the song, is the link valid?")
            return

        dl.download_song(self.song)

    def check_download(self, data=None):
        if not data:
            dl = SongDownloader()
            if dl.is_downloaded(self.song_id):
                self.ids.dl_button.text = "Redownload"
                self.ids.dl_button.disabled = False
                self.ids.dl_location_button.disabled = False
        else:
            if data["status"] == "downloading":
                self.ids.dl_button.text = "Downloading..."
                self.ids.dl_button.disabled = True
                self.ids.dl_location_button.disabled = True
            elif data["status"] == "error":
                ErrorPopup("There was an error when trying to download the song.")
                self.check_download()
            elif data["status"] == "finished":
                self.check_download()

    def edit_song(self):
        if self.song:
            edit = PopupSong(self._db, self.song)
            edit.bind(on_dismiss=lambda _: self.update_data(self.song_id))
            edit.open()

    def open_dl_folder(self):
        dl = SongDownloader()

        path = dl.get_song_path(self.song_id)

        if path:
            path = os.path.abspath(path)

            if os.getenv('WINDIR'):
                explorer = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
                subprocess.run([explorer, '/select,', path])
            else:
                import pyperclip

                pyperclip.copy(path)
                InfoPopup("The path has been copied to your clipboard.")

    def add_to_playlist(self):
        PopupAddToPlaylist(self._db, self.song_id).open()
