# PlexMediaCast
Provides ReST endpoints for casting Plex content to local devices

## Purpose
You may have found yourself wanting to automate the playing of Plex content on chromecast TVs or speakers:
- Play music in the morning as an alarm clock
- Begin binging Friends as soon as you walk through the door after work
- Turn on scary music when trick-or-treaters ring your doorbell
- Add QR codes or NFC tags to your DVD/CD cases to allow physical browsing of your library
- Add Plex voice commands to Google Assistant, Alexa, etc.

## Limitations
Music support is in it's early stages:
- Music cannot be shuffled
- Playing a specific Artist is not yet implemented (you must specify a song or album)

Random Movie support is limited:
- You can not yet specify a genre, actor, or director (you must give the movie title)

The service tends to time out or something, you will want to restart it each day until this is fixed.

For external use, including voice command support, a static IP address is needed from your ISP.

## Installation
1. Download/Install [Python 3](https://www.python.org/downloads/)
   - Include installation of PIP
   - Select to add Python to PATH (if using Windows)
2. Install project requirements
   - `pip install -r requirements.txt`
3. Populate config
4. Run `plexmediacast.py` as a service
   - On a windows machine, I recommend using Task Scheduler
   - Create a _Basic Task_
   - Trigger can be _when computer starts_
   - Action is _Start a program_ with **python.exe** as the program
   - Set the path to **plexmediacast.py** (in quotes) as an argument
   - Set _Start in_ the plexmediacast's parent directory
   - Open the _Properties_ dialog once you are finished
   - You likely want the task to run with the **highest privileges** whether the user is **logged on or not**
   - On the _Settings_ tab, you **will not want** to _Stop the task if it runs too long_

## Usage
### Voice Command Support
1. Ensure Plex Media Server is up and running
2. PlexMediaCast need not be running but the config must be populated
3. Turn on all Chromecast devices
   - All TVs, speakers, etc.
   - Any speaker groups that you want supported need to be created
   - Everything should be visible from the _cast_ option on your phone
4. Execute `autoiftttjsongen.py` to generate `Plex.json`
5. Review `voice_commands.txt` which s also generated within the `Output` directory
   - This lists the commands as well as the discovered devices
   - Check that each devices is listed and that the commands make sense
6. Use the output JSON with **AutoIFTTT**
