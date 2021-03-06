import os
import json
from datetime import datetime
from drop.errors import *


def warn(guild_id: int, user_id: int, user_name: str, author_id: int, author_name: str, channel_id: int, reason: str):
    dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    if not os.path.exists("data/servers/" + str(guild_id) + "/warns/"):
        os.makedirs("data/servers/" + str(guild_id) + "/warns/")
        # Checks if the folder for the guild exists. If it doesn't, create it.
    try:
        with open(f"data/servers/{guild_id}/warns/{user_id}.json", newline="\n", encoding='utf-8') as warn_file:
            warn_data = json.load(warn_file)
        # See if the user has been warned
    except FileNotFoundError:
        # User has not been warned yet
        with open(f"data/servers/{guild_id}/warns/{user_id}.json", 'w+', newline="\n", encoding='utf-8') as \
                warn_file:
            warn_data = ({
                'offender_name': user_name,
                'warns': [
                    {
                        'warner': author_id,
                        'warner_name': author_name,
                        'reason': reason,
                        'channel': str(channel_id),
                        'datetime': dt_string
                    }
                ]
            })
            json.dump(warn_data, warn_file)
    else:
        # If the script made it this far, then the user has been warned
        warn_data["offender_name"] = user_id
        new_warn = ({
            'warner': author_id,
            'warner_name': author_name,
            'reason': reason,
            'channel': str(channel_id),
            'datetime': dt_string
        })
        warn_data["warns"].append(new_warn)
        json.dump(warn_data, open(f"data/servers/{guild_id}/warns/{user_id}.json", "w+", newline="\n",
                                  encoding='utf-8'))


def get_warns(guild_id: int, user_id: int):
    try:
        with open(f"data/servers/{guild_id}/warns/{user_id}.json", 'r', newline="\n", encoding='utf-8') as \
                warn_file:
            return json.load(warn_file)
        # See if the user has been warned
    except FileNotFoundError:
        # User does not have any warns.
        return None


def write_warns(guild_id: int, user_id: int, new_warns: dict):
    try:
        with open(f"data/servers/{guild_id}/warns/{user_id}.json", 'w', newline="\n", encoding='utf-8') as \
                warn_file:
            json.dump(new_warns, warn_file)
    except FileNotFoundError:
        # User does not have any warns.
        return None


def get_warn(guild_id: int, user_id: int, warn_index: int):
    try:
        with open(f"data/servers/{guild_id}/warns/{user_id}.json", newline="\n", encoding='utf-8') as warn_file:
            warn_data = json.load(warn_file)
        # See if the user has been warned
    except FileNotFoundError:
        # User does not have any warns.
        return None
    warns = warn_data.get('warns')
    try:
        return warns[warn_index]
    except IndexError:
        raise IndexError(f"Warn index {warn_index} is not in current user's warns")


def remove_warn(guild_id: int, user_id: int, warn_index: int):
    warn_data = get_warns(guild_id, user_id)
    if warn_data is None:
        raise NoWarnError(f"User {user_id} does not have any warns: impossible to remove warns if they don't exist")
    warns = warn_data.get('warns')
    # do the whole removing process.
    warns = [x for x in warns if x != warns[warn_index]]
    warn_data["warns"] = warns
    if len(warns) <= 0:
        # no warns, might as well remove the file
        os.remove(f"data/servers/{guild_id}/warns/{user_id}.json")
    else:
        json.dump(warn_data, open(f"data/servers/{guild_id}/warns/{user_id}.json", 'w', newline="\n",
                                  encoding='utf-8'))


def clear_warns(guild_id: int, user_id: int):
    try:
        os.remove(f"data/servers/{guild_id}/warns/{user_id}.json")
    except FileNotFoundError:
        raise NoWarnError(f"User {user_id} does not have any warns: impossible to clear warns if they don't exist")


def edit_warn(guild_id: int, user_id: int, warn_index: int, new_reason: str):
    warns = get_warns(guild_id, user_id)
    warn_element = warns.get('warns')[warn_index]
    warn_element['reason'] = new_reason
    write_warns(guild_id, user_id, warns)

# warn stuff done
# lets do rules now


def get_rules(guild_id: int):
    rule_file = 'data/servers/' + str(guild_id) + '/rules.json'
    try:
        return json.load(open(rule_file, "r", encoding="utf-8", newline="\n"))
    except FileNotFoundError:
        raise NoRulesError(f"No rules had been set for guild {str(guild_id)}.")
    except json.JSONDecodeError:
        # wuh oh we may have a dead JSON file
        json.dump({}, open('data/servers/' + str(guild_id) + '/rules.json', 'w+', newline='\n', encoding="utf-8"))
        raise BrokenRulesError(f"Invalid JSON rule file for guild {str(guild_id)}: it has been reset.")


def get_rule(guild_id: int, index: str):
    return get_rules(guild_id).get(index.lower())


def set_rule(guild_id: int, index: str, description: str):
    try:
        rules = get_rules(guild_id)
    except NoRulesError:
        # no rules, make from scratch
        rules = {}
    rules[index.lower()] = description
    json.dump(rules, open('data/servers/' + str(guild_id) + '/rules.json', 'w+', newline='\n', encoding="utf-8"))


def pop_rule(guild_id: int, index: str):
    rules = get_rules(guild_id)
    filepath = 'data/servers/' + str(guild_id) + '/rules.json'
    with open(filepath, 'r') as file:
        try:
            rules.pop(index.lower())
        except KeyError:
            raise KeyError(f"Rule {index.lower()} does not exist for guild {guild_id}.")
        if rules is None:
            file.close()
            os.remove(filepath)
        else:
            json.dump(rules, open(filepath, 'w+'))
