import json
import os
import requests
import random
import discord
import tswift
import lyricsgenius


exampleServerConfig = {
    "prefix": "!",
    "share_error_logs": False,
    "asked_prefix": [],
    "inactivity_func": False,
    "inactivity_channels": [],
    "mute_role": 0,
    "disabled_commands": [],
    "disabled_cogs": [],
    "no_no_words": [],
    "tableflip": True,
    "language": "default"
}

exampleConfig = {}

with open("data/config.json", "r", encoding="utf-8", newline="\n") as f:
    bot_config = json.load(f)

langs = {}
for lang in os.listdir('lang/'):
    if lang.endswith('.json'):
        langname = lang.split('.')[0].lower()  # i need to stop doing these ass long code lines
        langs[langname] = json.load(open('lang/' + lang))


def get_github_config():
    global exampleConfig
    exampleConfig = json.loads(
        requests.get('https://raw.githubusercontent.com/AtlasC0R3/drop-bot/main/data/config.json').text)


def get_default_language(idx: int):
    return langs['default'][idx]


def get_all_languages():
    return langs.keys()


def get_language_str(language: str or int, idx: int):
    if type(language) is int:
        language = get_server_config(language, 'language', str)
    try:
        to_return = langs[language][idx]
        if not to_return:
            to_return = get_default_language(idx)
            # Sometimes people are lazy and might not want to translate a string.
            # or that i updated the bot and that the string couldn't be obtained
            # wait in that case it'd return indexerror, i'm dumb. like really dumb. like supremely dumb, holy wow.
    except KeyError or IndexError:
        return get_default_language(idx)
    return to_return


class TermColors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


SteamModes = {0: "disabled",
              1: "replace",
              2: "append"}


def get_discpy_version():
    return f'{discord.version_info.major}.{discord.version_info.minor}.{discord.version_info.micro}, ' \
           f'{discord.version_info.releaselevel} release'


def get_config_parameter(param, paramtype):
    config_param = bot_config.get(param)
    if config_param is None:
        config_param = exampleConfig.get(param)
        bot_config[param] = config_param
        json.dump(bot_config, open(f"data/config.json", "w+", encoding="utf-8", newline='\n'), indent=2)
    return paramtype(config_param)


try:
    genius = lyricsgenius.Genius(get_config_parameter('geniusApi', str), verbose=False, remove_section_headers=True,
                                 skip_non_songs=True, excluded_terms=["(Remix)", "(Live)"])
except TypeError:
    # Invalid token
    genius = None


def get_server_config(serverid, param, paramtype):
    try:
        with open(f"data/servers/{serverid}/config.json", "r", encoding="utf-8", newline="\n") as file:
            server_config = json.load(file)
            config_param = server_config.get(param)
            if config_param is None:
                config_param = exampleServerConfig.get(param)
                server_config[param] = config_param
                json.dump(server_config, open(f"data/servers/{serverid}/config.json", "w+", encoding="utf-8",
                                              newline='\n'))
            return paramtype(config_param)
    except FileNotFoundError:
        # No config exists for this server.
        if not os.path.exists(f"data/servers/{serverid}/"):
            os.makedirs(f"data/servers/{serverid}/")
        with open(f"data/servers/{serverid}/config.json", "w+", encoding="utf-8", newline='\n') as file:
            json.dump(exampleServerConfig, file, indent=2)
            return paramtype(exampleServerConfig.get(param))


def get_entire_server_config(serverid):
    try:
        with open(f"data/servers/{serverid}/config.json", "r", encoding="utf-8", newline="\n") as file:
            server_config = json.load(file)
            return server_config
    except FileNotFoundError:
        # No config exists for this server.
        with open(f"data/servers/{serverid}/config.json", "w", encoding="utf-8", newline='\n') as file:
            json.dump(exampleServerConfig, file, indent=2)
            return exampleServerConfig


def write_server_config(serverid, param, value):
    try:
        with open(f"data/servers/{serverid}/config.json", "r+", encoding="utf-8", newline="\n") as file:
            server_config = json.load(file)
            server_config[param] = value
            file.seek(0)
            json.dump(server_config, file, indent=2)
            file.truncate()
            return
    except FileNotFoundError:
        # No config exists for this server.
        with open(f"data/servers/{serverid}/config.json", "w", encoding="utf-8", newline='\n') as file:
            server_config = exampleServerConfig
            server_config[param] = value
            file.seek(0)
            json.dump(server_config, file, indent=2)
            file.truncate()
            return


def get_steam_played_game():
    steamapiconfig = get_config_parameter('steamApi', dict)
    for dictkey, value in steamapiconfig.items():
        if not value:
            if not dictkey == "excludedGames":
                print(f'Value {dictkey} undefined, playing Steam instead.\n'
                      f'Please disable "useSteamRecentlyPlayed" in config.json, '
                      f'or fill in the correct values in steamApi.\n'
                      f'If you need help, you can check out '
                      f'https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration')
                return 'Steam'
    userid = steamapiconfig.get('userId')
    key = steamapiconfig.get('key')
    steamurl = \
        f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1' \
        f'?key={key}' \
        f'&steamid={userid}' \
        f'&count=0'
    userdata = requests.get(steamurl)
    if userdata.status_code == 403:
        print("Invalid API key passed, falling back to playing Steam.\n"
              "Please disable \"useSteamRecentlyPlayed\" in config.json, "
              "or fill in the correct values in steamApi.\n"
              "If you need help, you can check out "
              "https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration")
        return 'Steam'
    elif userdata.status_code == 500:
        print("Invalid user ID passed, falling back to playing Steam.\n"
              "Please disable \"useSteamRecentlyPlayed\" in config.json, "
              "or fill in the correct values in steamApi.\n"
              "If you need help, you can check out "
              "https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration")
        return 'Steam'
    elif userdata.status_code != 200:
        print(f"Something went wrong with the API callout, falling back to playing Steam.\n"
              f"Error code {userdata.status_code}, in case you may need it.")
        return 'Steam'
    else:
        userdata = userdata.json()
        userdata = userdata.get('response').get('games')
        playedgame = random.choice(userdata).get('name')
        excludedgames = steamapiconfig.get('excludedGames')
        for no in excludedgames:
            if no.lower() in playedgame.lower():
                return get_steam_played_game()
        return playedgame


def get_steam_recently_played():
    steamapiconfig = get_config_parameter('steamApi', dict)
    for dictkey, value in steamapiconfig.items():
        if not value:
            if not dictkey == "excludedGames":
                print(f'Value {dictkey} undefined, playing Steam instead.\n'
                      f'Please disable "useSteamRecentlyPlayed" in config.json, '
                      f'or fill in the correct values in steamApi.\n'
                      f'If you need help, you can check out '
                      f'https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration')
                return 'Steam'
    userid = steamapiconfig.get('userId')
    key = steamapiconfig.get('key')
    steamurl = \
        f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1' \
        f'?key={key}' \
        f'&steamid={userid}' \
        f'&count=0'
    userdata = requests.get(steamurl)
    if userdata.status_code == 403:
        print("Invalid API key passed, falling back to playing Steam.\n"
              "Please disable \"useSteamRecentlyPlayed\" in config.json, "
              "or fill in the correct values in steamApi.\n"
              "If you need help, you can check out "
              "https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration")
        return 'Steam'
    elif userdata.status_code == 500:
        print("Invalid user ID passed, falling back to playing Steam.\n"
              "Please disable \"useSteamRecentlyPlayed\" in config.json, "
              "or fill in the correct values in steamApi.\n"
              "If you need help, you can check out "
              "https://github.com/AtlasC0R3/drop-bot/wiki/Configuring-the-Steam-integration")
        return 'Steam'
    elif userdata.status_code != 200:
        print(f"Something went wrong with the API callout, falling back to playing Steam.\n"
              f"Error code {userdata.status_code}, in case you may need it.")
        return 'Steam'
    else:
        playedgames = []
        userdata = userdata.json()
        userdata = userdata.get('response').get('games')
        for game in userdata:
            playedgames.append(game.get('name'))
        excludedgames = steamapiconfig.get('excludedGames')
        for no in excludedgames:
            for game in playedgames:
                if no.lower() in game.lower():
                    playedgames = [x for x in playedgames if x != game]
        return playedgames


def get_lyrics(artist, title):
    if genius:
        try:
            song = genius.search_song(title=title, artist=artist)
            # Fun fact: that's how I discovered that GHOST by Camellia (the song every beat saber player hates the most)
            # has lyrics, and that they lead to youtu.be/DkrzV5GIQXQ! how the actual fuck did i get here
            # I am now in shock and terrified. If anyone's into ARGs and reading this, well here you go.
            # It appears to be in Japanese though. Anyway, enough 3 minutes wasted.
        except requests.exceptions.HTTPError:
            song = None
            print("FIXME: Genius API token probably not working")
        if song:
            return song
    # no genius, woopsies
    song = tswift.Song(title=title, artist=artist)
    return song


def get_artist(artist):
    if genius:
        try:
            songs = genius.search_artist(artist, sort='popularity').songs
        except requests.exceptions.HTTPError:
            songs = None
            print("FIXME: Genius API token probably not working")
        if songs:
            lyrics = []
            for song in songs:
                lyric = song.lyrics.split('\n')
                lyrics.append([song.title, lyric[:5], song.url])
            artistname = songs[0].artist
            return ['Genius', [artistname, lyrics]]
    artistitem = tswift.Artist(artist)
    try:
        randsongs = random.sample(artistitem.songs, 5)
    except ValueError:
        # Not a valid artist. God freaking dammit.
        return None
    randlyrics = []
    artistname = ""
    for song in randsongs:
        lyric = get_lyrics(artist, song.title).load().lyrics.split('\n')
        randlyrics.append([song.title, lyric[:5], None])
        artistname = artistitem.songs[0].artist
    if not artistname:
        artistname = artist
    to_return = [artistname, randlyrics]
    return ['MetroLyrics', to_return]
