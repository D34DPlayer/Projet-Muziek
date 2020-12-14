import os

import music_tag
import youtube_dl

from ..logger import get_logger

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

logger = get_logger("yt-DL")


class SongDownloader(youtube_dl.YoutubeDL):
    def __init__(self, config=None):
        """Creates the SongDownloader object with the settings provided.

        :author: Carlos
        :param config: The SongDownloader configuration.
        """
        if config is None:
            config = {}
        self._config = {**default_config, **config, "logger": logger}

        self._video_info = None
        if not os.path.exists(self._config["download_dir"]):
            os.mkdir(self._config["download_dir"])

        super().__init__(self._config)

    def fetch_song(self, url: str):
        """Will extract the information from the provided link and return it.

        :author: Carlos
        :param url: The url of the video.
        :PRE: _
        :POST: Returns a dict with the video information if the url is correct, None if the url isn't.
        """
        info = self.extract_info(url=url, download=False)
        self._video_info = info
        return info

    def download_song(self, song_data):
        """Will download the previously fetched song and use the information from the database to choose
        where and how to store it.
        The song will be stored at "${download_dir}/${song_id}/${song_name} - ${group_name}.mp3"
        with the right metadata.

        :author: Carlos
        :param song_data: The information about the song stored in the database.
        :PRE: An url must have been fetched before.
        :POST: The song is downloaded to the right spot.
        :raises ValueError if there hasn't been a fetch_song before.
        """
        if not self._video_info:
            raise ValueError("A video needs to be fetched before it can be downloaded.")

        download_folder = os.path.join(self._config["download_dir"], str(song_data["song_id"]))
        if not os.path.exists(download_folder):
            os.mkdir(download_folder)

        file_name = f'{song_data["song_name"]} - {song_data["group_name"]}.%(ext)s'
        self.params["outtmpl"] = os.path.join(download_folder, file_name)

        self.prepare_filename(self._video_info)
        self.download([self._video_info["url"]])

        self.update_metadata(song_data)

    def is_downloaded(self, song_id: int):
        """Checks if a song has already been downloaded.

        :author: Carlos
        :param song_id: The song to check.
        :PRE: _
        :POST: Returns True if the song has already been downloaded, False otherwise.
        """
        download_folder = os.path.join(self._config["download_dir"], str(song_id))
        return os.path.isdir(download_folder) and bool(os.listdir(download_folder))

    def delete_song(self, song_id: int):
        """Deletes a song (if it has been downloaded) from the local storage.

        :author: Carlos
        :param song_id: The id of the song to delete.
        :PRE: _
        :POST: The song will be deleted if it has been downloaded.
        """
        song_path = self.get_song_path(song_id)
        if song_path:
            os.remove(song_path)

    def update_metadata(self, song_data):
        """Updates the metadata of the stored MP3 (if it exists) to fit the information stored in the database.

        :author: Carlos
        :param song_data: The information about the song stored in the database.
        :PRE: _
        :POST: The song metadata will be updated if it exists.
        """
        song_path = self.get_song_path(song_data["song_id"])

        if song_path:
            f = music_tag.load_file(song_path)
            f['artist'] = song_data["group_name"]
            f['genre'] = song_data["genre"]
            f['tracktitle'] = song_data["song_name"]
            f.save()

    def get_song_path(self, song_id):
        """Returns the path where the song has been downloaded.

        :author: Carlos
        :param song_id: The if of the song to look up.
        :PRE: _
        :POST: Returns the path if the song has been downlaoded, None otherwise.
        """
        if not self.is_downloaded(song_id):
            return None
        else:
            download_folder = os.path.join(self._config["download_dir"], str(song_id))
            song_name = os.listdir(download_folder)[0]

            return os.path.join(download_folder, song_name)

    def __getitem__(self, item):
        """Returns the item contained in the underlying video_data.

        :author: Carlos
        :param item: the key to the item to get.
        :PRE: _
        :POST: Returns None if no video has been fetched, the item from the video_info otherwise.
        """
        if not self._video_info:
            return None
        else:
            return self._video_info[item]
