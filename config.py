listen_on_port = 9138  # Access from outside local network requires port forwarding
tokens = []  # Specify your own tokens to secure incoming requests (Optional)
# Token Generator: https://www.random.org/passwords/?num=5&len=20&format=html&rnd=new

# Plex Media Server
pms_address = 'http://localhost:32400'
pms_token = 'INSERTTOKENHERE'
# To retrieve token: https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/

# Chromecast
default_device = 'Living Room TV'
default_video_device = 'Living Room TV'
default_music_device = 'Downstairs'

# AutoIFTTT JSON Generation
# Only required if you want voice command support
# These settings are good as-is but you may modify them to customize your experience
# Google reserves certain terms such as 'Play', 'Cast', and 'Stream'
play_show_verb = 'Plex'  # i.e. 'Watch', 'View', 'Binge'
play_movie_verb = 'Plex'  # i.e. 'Watch' 'View'
play_music_verb = 'Plex'  # i.e. 'Listen to'
voice_commands = {
    'show': [
        {
            'name': 'PVC Random Episode',
            'path': 'show?title={{TextField}}&random=true',
            'triggers': [
                '{verb} a random episode of $',
                '{verb} an episode of $'
            ],
            'response': 'Ok, playing a random episode $'
        },
        {
            'name': 'PVC Specific Episode',
            'path': 'show?title={{TextField}}&episode={{NumberField}}',
            'triggers': [
                '{verb} episode # of $',
            ],
            'response': 'Ok, playing an episode $'
        },
        {
            'name': 'PVC Next Episode',
            'path': 'show?title={{TextField}}',
            'triggers': [
                'Continue playing $',
                '{verb} the next episode of $'
            ],
            'response': 'Ok, playing the next episode $'
        },
    ],
    'movie': [
        {
            'name': 'PVC Movie',
            'path': 'movie?title={{TextField}}',
            'triggers': [
                '{verb} the movie $',
                '{verb} the film $'
            ],
            'response': 'Ok, playing $'
        }
    ],
    'artist': [
        {
            'name': 'PVC Artist',
            'path': 'artist?title={{TextField}}',
            'triggers': [
                '{verb} the artist $',
                '{verb} the band $',
                '{verb} the singer $',
                '{verb} the musician $',
                '{verb} music by $'
            ],
            'response': 'Ok, playing $'
        },
        {
            'name': 'PVC Album',
            'path': 'album?title={{TextField}}',
            'triggers': [
                '{verb} the album $'
            ],
            'response': 'Ok, playing $'
        },
        {
            'name': 'PVC Song',
            'path': 'song?title={{TextField}}',
            'triggers': [
                '{verb} the song $'
            ],
            'response': 'Ok, playing $'
        }
    ],
}
