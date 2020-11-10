import math
import getpass

getuser = getpass.getuser


def print_underline(*args, style='-'):
	txt = ' '.join(map(str, args)).rstrip()
	print(txt)
	print(style * math.ceil(len(txt) / len(style)))