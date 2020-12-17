# Muziek
[![codecov](https://codecov.io/gh/D34DPlayer/Projet-Muziek/branch/master/graph/badge.svg)](https://codecov.io/gh/D34DPlayer/Projet-Muziek)
[![CI](https://github.com/D34DPlayer/Projet-Muziek/workflows/CI/badge.svg?branch=master)](https://github.com/D34DPlayer/Projet-Muziek/actions?query=workflow%3ACI)
[![CD](https://github.com/D34DPlayer/Projet-Muziek/workflows/CD/badge.svg?branch=master)](https://github.com/D34DPlayer/Projet-Muziek/actions?query=workflow%3ACD)

Muziek is the music library management application for YouTube users.

## Usage
Muziek is an application that can be used either from a GUI or a CLI, to launch the GUI simply execute it without any arguments:
```
Usage:
  muziek [-d <PATH>]
  muziek [-d <PATH>] add (song | group | album)
  muziek [-d <PATH>] playlist <name> [-D | -e | -i | -s <song>...]
  muziek [-d <PATH>] list songs [-g <genre>] [-n <name>] [-G group]
  muziek [-d <PATH>] list group <name>
  muziek [-d <PATH>] list album <name>
  muziek [-d <PATH>] list (playlists | groups | albums)
  muziek [-d <PATH>] download song <name>
  muziek [-d <PATH>] youtube list [<name>]
  muziek [-d <PATH>] youtube import <name>
  muziek [-d <PATH>] youtube export <name>
  muziek -h | --help
  muziek --version

Options:
  -h --help             Show this screen.
  -d --database <PATH>  Path to the local storage [default: muziek.db].
  -s --song <song>      Song(s) to add to the playlist.
  -D --download         Download all the songs included in the playlist.
  -e --export           Exports the playlist.
  -i --import           Imports a playlist with the provided name.
  -g --genre <genre>    Filter the songs listed based on the genre.
  -G --group <group>    Filter the songs listed based on the group's name.
  -n --name <name>      Filter the songs listed based on the song's name.
  --version             Show version.
```

## Installation
### Dependencies
Muziek requires ffmpeg/libav to be able to download the songs: 
- On linux, ffmpeg should be available in your package manager:
- On Windows, you can install ffmpeg via [chocolatey](https://chocolatey.org/packages/ffmpeg), or download it manually from [here](https://ffmpeg.org/download.html#build-windows). 
### Getting an executable
You can get an already built executable for Windows or Linux with the [releases](https://github.com/D34DPlayer/Projet-Muziek/releases).
### Running it directly
You don't need to build an executable to run it, you can clone this repository, install the pytohn requirements and execute [main.py](https://github.com/D34DPlayer/Projet-Muziek/blob/master/main.py) with python as you would with the regular executable.
### Creating your own executable
If you want to build your own executable, follow the previous step and check that it works properly, then install pyinstaller with pip and finally run `pyinstaller main.spec` the executable will be located in the `dist` folder.
