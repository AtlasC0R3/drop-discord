import json
import os
import requests
import random
import discord


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
    "tableflip": True
}

exampleConfig = {}


def get_github_config():
    global exampleConfig
    print("Downloading default configuration from GitHub (not overwriting)...")
    exampleConfig = json.loads(
        requests.get('https://raw.githubusercontent.com/AtlasC0R3/drop-bot/main/data/config.json').text)
    print("done")


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
    with open("data/config.json", "r", encoding="utf-8", newline="\n") as f:
        bot_config = json.load(f)
        config_param = bot_config.get(param)
        if config_param is None:
            config_param = exampleConfig.get(param)
            bot_config[param] = config_param
            json.dump(bot_config, open(f"data/config.json", "w+", encoding="utf-8", newline='\n'), indent=2)
        return paramtype(config_param)


def get_server_config(serverid, param, paramtype):
    try:
        with open(f"data/servers/{serverid}/config.json", "r", encoding="utf-8", newline="\n") as f:
            server_config = json.load(f)
            config_param = server_config.get(param)
            if config_param is None:
                config_param = exampleServerConfig.get(param)
                server_config[param] = config_param
                json.dump(exampleServerConfig, open(f"data/servers/{serverid}/config.json", "w+", encoding="utf-8",
                                                    newline='\n'))
            return paramtype(config_param)
    except FileNotFoundError:
        # No config exists for this server.
        if not os.path.exists(f"data/servers/{serverid}/"):
            os.makedirs(f"data/servers/{serverid}/")
        with open(f"data/servers/{serverid}/config.json", "w+", encoding="utf-8", newline='\n') as f:
            json.dump(exampleServerConfig, f, indent=2)
            return paramtype(exampleServerConfig.get(param))


def get_entire_server_config(serverid):
    try:
        with open(f"data/servers/{serverid}/config.json", "r", encoding="utf-8", newline="\n") as f:
            server_config = json.load(f)
            return server_config
    except FileNotFoundError:
        # No config exists for this server.
        with open(f"data/servers/{serverid}/config.json", "w", encoding="utf-8", newline='\n') as f:
            json.dump(exampleServerConfig, f, indent=2)
            return exampleServerConfig


def write_server_config(serverid, param, value):
    try:
        with open(f"data/servers/{serverid}/config.json", "r+", encoding="utf-8", newline="\n") as f:
            server_config = json.load(f)
            server_config[param] = value
            f.seek(0)
            json.dump(server_config, f, indent=2)
            f.truncate()
            return
    except FileNotFoundError:
        # No config exists for this server.
        with open(f"data/servers/{serverid}/config.json", "w", encoding="utf-8", newline='\n') as f:
            server_config = exampleServerConfig
            server_config[param] = value
            f.seek(0)
            json.dump(server_config, f, indent=2)
            f.truncate()
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
