import json
import os
import requests


exampleServerConfig = {
    "prefix": "!",
    "share_error_logs": False,
    "asked_prefix": [],
    "inactivity_func": False,
    "inactivity_channels": [],
    "mute_role": 0,
    "disabled_commands": [],
    "no_no_words": []
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
