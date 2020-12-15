import os
import subprocess

from kivy.lang.builder import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button

from .popup_song import PopupSong
from .popup_playlist import PopupAddToPlaylist
from .utils import ErrorPopup, InfoPopup
from ..database import DBMuziek, format_duration
from ..downloader import SongDownloader

Builder.load_file("libs/graphical_interface/details_song.kv")


class DetailsSong(BoxLayout):
    def __init__(self, db: DBMuziek, song_id: int, back_action=None, **kwargs):
        super(DetailsSong, self).__init__(**kwargs)
        self._db = db
        self.song_id = song_id

        self.song = None

        self.update_data(self.song_id)

        if back_action:
            btn = Button(text="Go back")
            btn.bind(on_release=lambda _: back_action())
            self.add_widget(btn)

    def update_data(self, song_id):
        self.song_id = song_id
        self.song = self._db.get_song(song_id=song_id)

        if self.song:
            self.ids.song_name.text = self.song["song_name"]
            self.ids.duration.text = format_duration(self.song["duration"])
            self.ids.link.text = self.song["link"]
            self.ids.genre.text = self.song["genre"]
            self.ids.group_name.text = self.song["group_name"]

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
        edit = PopupSong(self._db, self.song)
        edit.bind(on_dismiss=lambda _: self.update_data(self.song_id))
        edit.open()

    def open_dl_folder(self):
        dl = SongDownloader()

        path = dl.get_song_path(self.song_id)

        if path:
            if os.getenv('WINDIR'):
                explorer = os.path.join(os.getenv('WINDIR'), 'explorer.exe')
                subprocess.run([explorer, '/select,', path])
            else:
                import pyperclip

                pyperclip.copy(path)
                InfoPopup("The path has been copied to your clipboard.")

    def add_to_playlist(self):
        PopupAddToPlaylist(self._db, self.song_id).open()
