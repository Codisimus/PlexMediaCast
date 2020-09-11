import json
import os

import pychromecast
import requests

import config
from devicecache import DeviceCache
from mediatype import MediaType

voice_commands = []
video_devices = []
music_devices = []


def is_video_device(cast):
    return cast.cast_type == pychromecast.CAST_TYPE_CHROMECAST and (
            'Nest' not in cast.model_name or 'Hub' in cast.model_name)


def add_video_device(cast_name):
    if cast_name == config.default_video_device:
        cast_name += ' (default)'
    video_devices.append(cast_name)


def add_music_device(cast_name):
    if cast_name == config.default_music_device:
        cast_name += ' (default)'
    music_devices.append(cast_name)


def generate_json():
    public_ip = json.loads(requests.get('http://httpbin.org/ip').text)['origin']

    obj = {
        "base_url": "http://" + public_ip + ":" + str(config.listen_on_port) + "/",
        "token": config.tokens[0] if len(config.tokens) > 0 else "",
        "applets": []
    }

    for cast in DeviceCache.get_devices():
        obj['applets'].extend(generate_applets(MediaType.artist, cast.name))
        if is_video_device(cast):
            add_video_device(cast.name)
            obj['applets'].extend(generate_applets(MediaType.show, cast.name))
            obj['applets'].extend(generate_applets(MediaType.movie, cast.name))
        else:
            add_music_device(cast.name)

    with open("Output/Plex.json", "w") as f:
        f.write(json.dumps(obj, indent=4))


def generate_applets(media_type, cast_name):
    applets = []
    for applet_config in config.voice_commands[media_type.name]:
        applets.append(generate_applet(applet_config, media_type, cast_name))
    return applets


def generate_applet(applet_config, media_type, cast_name):
    return {
        'name': applet_config['name'] + ' (' + cast_name + ')',
        'path': applet_config['path'] + '&device=' + cast_name,
        'triggers': generate_commands(media_type, cast_name, applet_config['triggers']),
        'response': applet_config['response'] + ' on ' + cast_name
    }


def generate_commands(media_type, cast_name, command_strings):
    if media_type == MediaType.show:
        verb = config.play_show_verb
    elif media_type == MediaType.movie:
        verb = config.play_movie_verb
    elif media_type == MediaType.artist:
        verb = config.play_music_verb
    else:
        verb = 'Plex'
    commands = []
    for command in command_strings:
        command = command.replace('{verb}', verb)
        commands.append(command + ' on ' + cast_name)
        commands.append(command + ' on the ' + cast_name)
        if cast_name == media_type.default_device:
            voice_commands.append(command)
            commands.append(command)
    return commands


def generate_documentation():
    with open('Output/voice_commands.txt', 'w' if os.path.exists('Output/voice_commands.txt') else 'x') as f:
        f.write('Voice Commands:\n\t')
        f.writelines('\n\t'.join(line for line in voice_commands))
        f.write('\n\nA device may be specified with "on {name}" or "on the {name}" at the end of any command\n')
        f.write('\nMusic Only Devices:\n\t')
        f.writelines('\n\t'.join(line for line in music_devices))
        f.write('\n\nVideo and Music Devices:\n\t')
        f.writelines('\n\t'.join(line for line in video_devices))


if not os.path.isdir('Output'):
    os.mkdir('Output')
generate_json()
generate_documentation()
