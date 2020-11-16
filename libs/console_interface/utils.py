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

    length = math.ceil(math.log10(last))
    for sid, name, *song in songs:
        text = f'{sid:>{length}}. {name}'
        if nargs > 2: # duration
            text += f' ({format_duration(song[0])})'
        if nargs > 3: # group
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
