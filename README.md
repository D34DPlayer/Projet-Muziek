# Muziek
[![codecov](https://codecov.io/gh/D34DPlayer/Projet-Muziek/branch/master/graph/badge.svg)](https://codecov.io/gh/D34DPlayer/Projet-Muziek)

Muziek is the music library management application for YouTube users.

## Usage
```
Usage:
  main.py [-d <PATH>] add (song | group | album)
  main.py [-d <PATH>] playlist <name> [-s <song>]...
  main.py [-d <PATH>] list songs [-g <genre>] [-n <name>] [-G group]
  main.py [-d <PATH>] list group <name>
  main.py [-d <PATH>] list album <name>
  main.py [-d <PATH>] list playlists
  main.py [-d <PATH>] download song <name>
  main.py -h | --help
  main.py --version

Options:
  -h --help             Show this screen.
  -d --database <PATH>  Path to the local storage [default: muziek.db].
  -s --song <song>      Song to add to the playlist.
  -g --genre <genre>    Filter the songs listed based on the genre.
  -G --group <group>    Filter the songs listed based on the group's name.
  -n --name <name>      Filter the songs listed based on the song's name.
  --version             Show version.
```
