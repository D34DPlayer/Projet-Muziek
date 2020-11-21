import youtube_dl

default_config = {
    "quiet": True,
    "format": "bestaudio/best",
    'postprocessors': [{
        'key': 'FFmpegExtractAudio',
        'preferredcodec': 'mp3',
        'preferredquality': '192',
    }]
}


class Downloader(youtube_dl.YoutubeDL):
    def __init__(self, config: dict = {}):
        self._config = {**default_config, **config}

        super().__init__(self._config)

    def validate_url(self, url: str):
        try:
            info = self.extract_info(url=url, download=False)
        except youtube_dl.utils.UnavailableVideoError:
            return None
        else:
            return info
