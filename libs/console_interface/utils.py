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
