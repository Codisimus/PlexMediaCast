from plexapi.server import PlexServer

import config
from util import *

pms = PlexServer(config.pms_address, config.pms_token)


class MismatchedLibrariesError(Exception):
    pass


def full_library():
    return pms.library


def all_libraries():
    return pms.library.sections()


def get_libraries(names):
    libraries = []
    for name in names:
        libraries.append(get_library(name))
        return libraries


def get_library(name):
    library = pms.library.section(name)
    if not library:
        library = find_by_attr(all_libraries(), 'title', name, case_sensitive=False)
        if not library:
            raise NotFoundError('Library ' + name)
    return library


def get_libraries_of_type(media_type):
    libraries = []
    for library in all_libraries():
        if library.type == media_type:
            libraries.append(library)
    return libraries


def validate_song_details(library, song, album, artist):
    if album:
        valid = False
        for result in get_album(library, album):
            if result.title == song.parentTitle:
                valid = True
                break
        if not valid:
            return False
    if artist:
        valid = False
        for result in get_artist(library, artist):
            if result.title in [song.originalTitle, song.grandparentTitle]:
                valid = True
                break
        if not valid:
            return False
    return True


def validate_album_details(library, album, artist):
    if artist:
        valid = False
        for result in get_artist(library, artist):
            if result.title == album.parentTilte:
                valid = True
                break
        return valid
    return True


def on_deck(library, show):
    for item in library.onDeck():
        if item.type == 'episode' and item.grandparentKey == show.key:
            return item
    for season in show.seasons():
        if season.seasonNumber > 0:
            return season.episodes()[0]


def get_artist(library, name):
    return library.search(title=name, libtype='artist')


def get_album(library, name):
    return library.search(title=name, libtype='album')


def get_song(library, name):
    return library.search(title=name, libtype='track')
