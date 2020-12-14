import base64
import getpass
import json
import math
import re
import zlib
from typing import List
from ..database import format_duration

getuser = getpass.getuser


def print_underline(*args, style='-', **kwargs):
    """Prints an underlined message to the console.

    :param args: Anything you want to display to the console.
    :param style: The underline style.
    :param kwargs: Optionnals given to the function "print".
    """
    sep = kwargs.pop('sep', ' ')
    txt = sep.join(map(str, args))
    length = max(len(line.rstrip()) for line in txt.splitlines())

    print(txt, style * math.ceil(length / len(style)), sep='\n', **kwargs)


def display_songs(songs: List):
    """Prints a list of songs on the screen.

    :param songs: A list of songs to display. Each song is a dict made of:
        - song_id:`int`     Optional. The song's id.
        - song_name:`str`   Required. The song's title.
        - duration:`int`    Optional. The song's duration.
        - group_name:`str`  Optional. The song's group.
        - featuring:`list`  Optional. A list of groups that have been featured in the song.
    """
    if len(songs) == 0:
        print('<empty>')
        return

    if "song_id" not in songs[0]:
        last = len(songs)
        songs = [{"song_id": i, **s} for i, s in enumerate(songs, 1)]
    else:
        last = max(s["song_id"] for s in songs)

    length = math.floor(math.log10(last)) + 1
    for song in songs:
        text = f'{song["song_id"]:>{length}}. {song["song_name"]}'
        if "duration" in song:                          # duration
            text += f' ({format_duration(song["duration"])})'
        if "group_name" in song:                        # group
            text += f' - {song["group_name"]}'
        if "featuring" in song and song["featuring"]:   # featuring
            text += f' (ft. {", ".join([f["group_name"] for f in song["featuring"]])})'

        print(text)


def question(name: str, default: str = None):
    if default:
        return input(f"{name} [{default}]:") or default
    else:
        result = ""
        while not result:
            result = input(f"{name}:")
        return result


def question_choice(name: str, choices: List[str]):
    if not choices:
        return None
    result = ""
    while result not in choices:
        result = input(f"{name} [{'/'.join(choices)}]:")
    return result


def pagination(total: int, page: int) -> int:
    """Display a pagination, prompt the user for a new page and return it.

    :author: Mathieu
    :param total: The total number of pages.
    :param page: The current page.
    :return: The new page to show. -1 if the user wants to quit.
    """
    if total > 1:
        pages = []

        anchors = [1, page, total]
        anchors = list(sorted(set(anchors)))  # removes duplicates
        for i in range(len(anchors) - 1):
            a, b = anchors[i], anchors[i + 1]
            if b - a < 6:
                # straight a → b
                pages.extend(str(i) for i in range(a, b))
            else:
                # add the first 3 pages
                pages.extend(str(i) for i in range(a, a + 3))
                pages.append('..')
                # add the last 2 pages, the third one is included by the next iteration
                pages.extend(str(i) for i in range(b - 2, b))

        # add the last page bc it's not included in the loop
        pages.append(str(total))

        if str(page) in pages:
            pages[pages.index(str(page))] = f'[{page}]'

        print(f"Pages: {' '.join(pages)}")

        page = 0
        while not 0 < page <= total:
            page = input('Display another page: ').strip()

            if len(page) == 0:
                return -1

            page = int(page) if page.isdecimal() else 0

        return page

    return -1


def strip_brackets(string: str) -> str:
    """Removes brackets and its content.

    :param string: A string with brackets.
    :return: The input string without the brackets and its content.
    """
    return re.sub(r'(?:(\()|(\{)|(\[)).*?(?(1)\)|(?(2)\}|\]))', '', string).strip()


def _choose(query, _type: str, item: str):
    """If multiple "type" have the same name, asks the user which one should be used.

    :author: Carlos
    :param query: A list of "type" to choose from.
    :param _type: What are we handling.
    :param item: The item that should be used to choose.
    :return: The song chosen by the user.
    """

    if not query or not isinstance(query, List):
        return query

    if len(query) == 1:
        return query[0]
    else:
        values = [s[item] for s in query]
        print(f"{len(query)} {_type} were found with that name from the groups:")

        counter = 1
        for value in values:
            print(f" {counter} : {value}")
            counter += 1
        number = question_choice("Choose one", [str(en[0]) for en in enumerate(values, 1)])

        return query[int(number) - 1]


def choose_album(album_query):
    return _choose(album_query, "albums", "group_name")


def choose_song(song_query):
    return _choose(song_query, "songs", "group_name")


def encode(data) -> str:
    """Transforms a python object into a shareable string.

    :param data: Data to encode.
    :return: Encoded data
    """
    json_str = json.dumps(data)
    comp_bytes = zlib.compress(json_str.encode("utf-8"))
    encoded_bytes = base64.b64encode(comp_bytes)
    return str(encoded_bytes, "utf-8")


def decode(data: str):
    """Transforms a shareable string into a python object.

    :param data: string to decode.
    :return: Data decoded.
    """
    decoded_bytes = base64.b64decode(data.encode("utf-8"))
    decomp_byptes = zlib.decompress(decoded_bytes)
    json_str = str(decomp_byptes, "utf-8")
    return json.loads(json_str)


def get_info_from_title(title):
    elements = strip_brackets(title).split('-')
    if len(elements) < 2:
        return "Unknown", elements[0].strip()
    else:
        return tuple(el.strip() for el in elements[:2])
