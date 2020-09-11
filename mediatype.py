import random

from devicecache import DeviceCache
from pmshelper import *
from util import *


class MediaType:
    types = []
    artist = None
    movie = None
    show = None

    def __init__(self, name, display_name, default_device):
        self.name = name
        self.display_name = display_name
        self.default_device = default_device

    def get_device(self):
        return DeviceCache.get_device(self.default_device)

    def get_params(self):
        raise UnimplementedError

    def find_media_with_ifttt_fix(self, params, libraries):
        try:
            return self.find_media(params, libraries)
        except NotFoundError as e:
            words = params.title.split(' ')
            if len(words) <= 1:
                raise e
            params.title = ' '.join(words[1:])  # IFTTT fix
            # Related post: https://www.reddit.com/r/ifttt/comments/77ox7c/help_needed_google_assistant_text_ingredient/
            return self.find_media(params, libraries)

    def find_media(self, params, libraries):
        raise UnimplementedError

    def media_details(self, media):
        return {
            'summary': media.summary,
            'thumb': media.thumb,
            'title': media.title,
            'type': media.type
        }

    @classmethod
    def get_media_types(cls):
        return cls.types

    @classmethod
    def get_media_type_of_libraries(cls, libraries):
        return get_attr(cls, libraries[0].type)

    @classmethod
    def get_media_type_of_media(cls, media):
        if media.listType == 'audio':
            return cls.artist
        elif media.type == 'movie':
            return cls.movie
        else:
            return cls.show


class Artist(MediaType):
    def __init__(self):
        super().__init__('artist', 'Music', config.default_music_device)

    def get_params(self):
        params = Object()
        params.artist = get_param('artist')
        params.album = get_param('album')
        params.song = get_param('song')
        return params

    def find_media(self, params, libraries):
        for library in libraries:
            # Specific Song
            if params.song:
                for song in get_song(library, params.song):
                    if validate_song_details(library, song, params.album, params.artist):
                        return song
            # Specific Album
            elif params.album:
                for album in get_album(library, params.album):
                    if validate_album_details(library, album, params.artist):
                        return album
            # Specific Artist
            elif params.artist:
                results = get_artist(library, params.artist)
                if results:
                    # TODO: Create shuffled Playlist with songs from each Library
                    return results[0]
            else:
                # TODO: Create shuffled Playlist with songs from each Library
                return library.all()[0]
        string = '{'
        if params.artist:
            string += 'artist: ' + params.artist + ','
        if params.album:
            string += 'album: ' + params.album + ','
        if params.song:
            string += 'song: ' + params.song + ','
        string = string[:-1] + '}'
        raise NotFoundError(string)

    def media_details(self, media):
        details = super().media_details(media)
        if media.type == 'artist':
            details['artist'] = media.title
            details['album_count'] = len(media.albums())
            details['genre'] = [genre.tag for genre in media.genres]
        elif media.type == 'album':
            details['artist'] = media.parentTitle
            details['genre'] = [genre.tag for genre in media.genres]
            details['album'] = media.title
            details['year'] = media.year
            details['song_count'] = len(media.tracks())
        elif media.type == 'track':
            details['artist'] = media.originalTitle if media.originalTitle else media.grandparentTitle
            details['album'] = media.parentTitle
            details['track_number'] = media.index
            details['song'] = media.title
            details['length'] = millis2minutesseconds(media.duration)
            details['year'] = media.year
        return details


class Movie(MediaType):
    def __init__(self):
        super().__init__('movie', 'Movies', config.default_video_device)

    def get_params(self):
        params = Object()
        params.title = get_param('title', required=True)
        return params

    def find_media(self, params, libraries):
        for library in libraries:
            results = library.search(params.title, libtype=self.name, maxresults=1)
            if results:
                return results[0]
        raise NotFoundError('Movie ' + params.title)

    def media_details(self, media):
        details = super().media_details(media)
        details['tag_line'] = media.tagline
        details['genre'] = [genre.tag for genre in media.genres]
        details['year'] = media.year
        details['content_rating'] = media.contentRating
        details['length'] = millis2minutes(media.duration)
        return details


class Show(MediaType):
    def __init__(self):
        super().__init__('show', 'TV Shows', config.default_video_device)

    def get_params(self):
        params = Object()
        params.title = get_param('title', required=True)
        if params.title.startswith('of '):  # IFTTT fix
            # Related post: https://www.reddit.com/r/ifttt/comments/77ox7c/help_needed_google_assistant_text_ingredient/
            params.title = params.title[3:]
        if has_param('episode'):
            episode = get_param('episode')
            params.season_number = int(episode[:-2])
            params.episode_number = int(episode[-2:])
        else:
            params.season_number = get_param('season_number', integer=True)
            params.episode_number = get_param('episode_number', integer=True)
            params.episode_name = get_param('episode_name')
        params.random = get_param('random', boolean=True)
        return params

    def find_media(self, params, libraries):
        for library in libraries:
            # Specific Show
            for show in library.search(params.title, libtype=self.name):
                episode = None
                # Specific Episode
                if params.episode_number:
                    season = params.season_number if params.season_number else 1
                    episode = show.episode(season=season, episode=params.episode_number)
                elif params.episode_name:
                    episode = show.episode(params.episode_name)
                # Random Episode
                elif params.random:
                    if params.season_number:
                        episode = random.choice(show.season(params.season_number).episodes())
                    else:
                        episodes = show.episodes()
                        random.shuffle(episodes)
                        for e in episodes:
                            if e.seasonNumber != 0:
                                episode = e
                # Next Episode
                else:
                    episode = on_deck(library, show)

                if episode:
                    return episode
        raise NotFoundError('Show ' + params.title)

    def media_details(self, media):
        details = super().media_details(media)
        details['content_rating']: media.contentRating
        if media.type == 'episode':
            details['year'] = media.year
            details['length'] = millis2minutes(media.duration)
            details['show'] = media.grandparentTitle
            details['season_number'] = int(media.parentIndex)
            details['episode_number'] = int(media.index)
        return details


MediaType.artist = Artist()
MediaType.types.append(MediaType.artist)
MediaType.movie = Movie()
MediaType.types.append(MediaType.movie)
MediaType.show = Show()
MediaType.types.append(MediaType.show)
