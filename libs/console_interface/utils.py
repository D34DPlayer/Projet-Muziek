import math
import getpass

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