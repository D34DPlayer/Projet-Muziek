import youtube_dl
import os


default_config = {
    "quiet": True,
    "format": "bestaudio/best",
    "postprocessors": [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }],
    "download_dir": "./songs",
    "ignoreerrors": True,
    "no_color": True
}


class SongDownloader(youtube_dl.YoutubeDL):
    def __init__(self, logger=None, config: dict = {}):
        self._config = {**default_config, **config}
        if logger:
            self._config["logger"] = logger

        self._video_info = None
        if not os.path.exists(self._config["download_dir"]):
            os.mkdir(self._config["download_dir"])

        super().__init__(self._config)

    def fetch_song(self, url: str):
        info = self.extract_info(url=url, download=False)
        self._video_info = info
        return info

    def download_song(self, song_data):
        if not self._video_info:
            raise ValueError("A video needs to be fetched before it can be downloaded.")

        download_folder = os.path.join(self._config["download_dir"], str(song_data["song_id"]))
        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

        file_name = f'{song_data["song_name"]} - {song_data["group_name"]}.mp3'
        self.params["outtmpl"] = os.path.join(download_folder, file_name)

        self.prepare_filename(self._video_info)
        self.download([self._video_info["url"]])

    def is_downloaded(self, song_id: int):
        download_folder = os.path.join(self._config["download_dir"], str(song_id))
        return os.path.isdir(download_folder) and os.listdir(download_folder)

    def delete_song(self, song_id: int):
        download_folder = os.path.join(self._config["download_dir"], str(song_id))
        if self.is_downloaded(song_id):
            for file in os.listdir(download_folder):
                os.remove(os.path.join(download_folder, file))
