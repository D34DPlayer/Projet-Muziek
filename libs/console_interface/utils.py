import math
import getpass
from typing import List

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


def display_songs(songs: List[tuple]):
    """Prints a list of songs on the screen.

    :param songs: A list of songs to display. Each song is a tuple made of:
        - id:`int`       Optional. The song's id.
        - name:`str`     Required. The song's title.
        - duration:`int` Optional. The song's duration.
        - group:`str`    Optional. The song's group.
    """
    if len(songs) == 0:
        print('<empty>')
        return

    nargs = len(songs[0])
    if not isinstance(songs[0][0], int):
        last = len(songs)
        songs = ((i, *s) for i, s in enumerate(songs, 1))
        nargs += 1
    else:
        last = max(s[0] for s in songs)

    length = math.floor(math.log10(last)) + 1
    for sid, name, *song in songs:
        text = f'{sid:>{length}}. {name}'
        if nargs > 2:  # duration
            text += f' ({format_duration(song[0])})'
        if nargs > 3:  # group
            text += f' - {song[1]}'

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
    result = ""
    while result not in choices:
        result = input(f"{name} [{'/'.join(choices)}]:")
    return result


def format_duration(duration: int = None):
    if duration is None:
        return '??:??'

    return '{}:{}'.format(*divmod(duration, 60))


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


def choose_song(song_query):
    """If multiple songs have the same name, asks the user which one should be used.

    :author: Carlos
    :param song_query: A list of songs to choose from.
    :return: The song chosen by the user.
    """

    if not song_query:
        return song_query

    if len(song_query) == 1:
        return song_query[0]
    else:
        groups = [s["group_name"] for s in song_query]
        print(f"{len(song_query)} songs where found with that name from the groups:")

        counter = 1
        for group in groups:
            print(f" {counter} : {group}")
            counter += 1
        number = question_choice("Choose one", [str(i + 1) for i in range(len(groups))])

        return song_query[int(number) - 1]
