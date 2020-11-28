import json
import os


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


class bcolors:
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
        return paramtype(bot_config.get(param))


def get_server_config(serverid, param, paramtype):
    try:
        with open(f"data/servers/{serverid}/config.json", "r", encoding="utf-8", newline="\n") as f:
            server_config = json.load(f)
            return paramtype(server_config.get(param))
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
