import logging
import traceback
from threading import Thread

from flask import Flask, json
from pychromecast.controllers.plex import PlexController

import config
import pmshelper as pms
from devicecache import DeviceCache
from mediatype import MediaType
from pmshelper import MismatchedLibrariesError
from util import *

logging.basicConfig(filename="PlexMediaCast.log")

api = Flask(__name__)


@api.errorhandler(MissingParamError)
def handle_missing_param(e):
    msg = e.name + ' is a required parameter'
    logging.warning(msg)
    return msg, 400


@api.errorhandler(InvalidTokenError)
def handle_invalid_token(e):
    msg = 'Invalid Token'
    logging.warning(msg)
    return msg, 401


@api.errorhandler(MismatchedLibrariesError)
def handle_mismatched_library(e):
    msg = 'A common media type was not found across specified libraries'
    logging.warning(msg)
    return msg, 400


@api.errorhandler(NotFoundError)
def handle_not_found(e):
    msg = e.name + ' Not Found'
    logging.warning(msg)
    return msg, 400


@api.errorhandler(UnimplementedError)
def handle_unimplemented(e):
    return 'Unsupported', 501


@api.errorhandler(Exception)
def handle_uncaught(e):
    traceback.print_exc()
    return 'An Exception has occurred on the server: ' + str(e), 500


@api.route('/devices', methods=['GET'])
def get_devices():
    validate_token()
    return json.dumps([cast.device.friendly_name for cast in DeviceCache.get_devices()])


@api.route('/libraries', methods=['GET'])
def get_libraries():
    validate_token()
    return json.dumps([library.title for library in pms.all_libraries()])


@api.route('/mediatypes', methods=['GET'])
def get_media_types():
    validate_token()
    return json.dumps([media_type.name for media_type in MediaType.types])


@api.route('/play', methods=['GET'])
def play_media():
    validate_token()
    media = find_media(libraries=find_libraries())
    return cast_media(media)


@api.route('/artist', methods=['GET'])
def play_artist():
    validate_token()
    media = find_media(media_type=MediaType.artist, artist=get_param('name'))
    return cast_media(media)


@api.route('/album', methods=['GET'])
def play_album():
    validate_token()
    media = find_media(media_type=MediaType.artist, album=get_param('name', 'title'))
    return cast_media(media)


@api.route('/song', methods=['GET'])
def play_song():
    validate_token()
    media = find_media(media_type=MediaType.artist, song=get_param('name', 'title'))
    return cast_media(media)


@api.route('/movie', methods=['GET'])
def play_movie():
    validate_token()
    media = find_media(MediaType.movie)
    return cast_media(media)


@api.route('/show', methods=['GET'])
def play_show():
    validate_token()
    media = find_media(MediaType.show)
    return cast_media(media)


def validate_token():
    if config.tokens and get_param('token', required=True) not in config.tokens:
        raise InvalidTokenError


def find_libraries():
    if has_param('library'):
        libraries = pms.get_libraries(get_param('library', split=True))
        for library in libraries:
            if library.type != libraries[0].type:
                raise MismatchedLibrariesError
    else:
        media_type = get_param('mediatype', required=True)
        libraries = pms.get_libraries_of_type(media_type)
        if len(libraries) == 0:
            raise NotFoundError('MediaType ' + media_type)
    return libraries


def find_media(media_type=None, libraries=None, **kwargs):
    if not media_type:
        media_type = MediaType.get_media_type_of_libraries(libraries)
    params = media_type.get_params()
    for key, value in kwargs.items():
        if value and not getattr(params, key):
            setattr(params, key, value)
    if not libraries:
        libraries = [pms.full_library()]
    return media_type.find_media(params, libraries)


def cast_media(media):
    media_type = MediaType.get_media_type_of_media(media)
    response = media_type.media_details(media)
    if get_param('cast', boolean=True, default=True):
        cast = find_device(media_type)
        Thread(target=cast_media_to, args=(cast, media)).start()
        response['device'] = cast.name
    return json.dumps(response)


def find_device(media_type=None):
    if media_type and not has_param('device'):
        return media_type.get_device()
    return DeviceCache.get_device(get_param('device', default=config.default_device))


def cast_media_to(cast, media):
    try:
        cast.wait()
        pc = PlexController()
        cast.register_handler(pc)
        pc.play_media(media)
    except Exception as e:
        logging.error(e)


if __name__ == '__main__':
    api.run(host='0.0.0.0', port=str(config.listen_on_port))
