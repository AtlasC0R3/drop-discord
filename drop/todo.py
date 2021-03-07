import os
import json
from datetime import datetime

dir_path = "data/todo/"


def init_todo(user_id: int, force_init=False):
    file_path = dir_path + f"{user_id}.json"
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)
    if (not os.path.exists(file_path)) or force_init:
        with open(file_path, 'w+', newline="\n", encoding='utf-8') as todo_file:
            todo_data = []
            json.dump(todo_data, todo_file)


def get_todos(user_id: int):
    file_path = dir_path + f"{user_id}.json"
    try:
        with open(file_path, newline="\n", encoding='utf-8') as todo_file:
            todo_data = json.load(todo_file)
            # does the user have to-do stuff
            # oh god pycharm things to-do without '-' is always a to-do thing to do
    except FileNotFoundError:
        # nothing generated yet
        init_todo(user_id=user_id)  # mess.
        todo_data = get_todos(user_id)  # this works
    except json.JSONDecodeError:
        init_todo(user_id, True)
        todo_data = get_todos(user_id)
        # God dammit. Had to reinitialize this.
    return todo_data


def get_todo(user_id: int, index: int):
    return get_todos(user_id).get(index)


def edit_todo(user_id: int, index: int, description: str):
    todo_data = get_todos(user_id)
    new_todo = {
        'desc': description,
        'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    }
    todo_data[index] = new_todo
    with open(f"data/todo/{user_id}.json", 'w+', newline="\n", encoding='utf-8') as todo_file:
        json.dump(todo_data, todo_file)
    return


def add_todo(user_id: int, description: str):
    todo_data = get_todos(user_id)
    new_todo = {
        'desc': description,
        'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    }
    todo_data.append(new_todo)
    with open(f"data/todo/{user_id}.json", 'w+', newline="\n", encoding='utf-8') as todo_file:
        json.dump(todo_data, todo_file)
        todo_file.close()


def rm_todo(user_id: int, index: int):
    todo_data = get_todos(user_id)
    try:
        todo_data.pop(index)
    except IndexError:
        raise IndexError(f"Index {index} does not exist in to-do data for user {user_id}")
    with open(f"data/todo/{user_id}.json", 'w+', newline="\n", encoding='utf-8') as todo_file:
        json.dump(todo_data, todo_file)
        todo_file.close()


# guild stuff


def get_guild_todos(guild_id: int):
    try:
        with open(f"data/servers/{guild_id}/todo.json", newline="\n", encoding='utf-8') as todo_file:
            return json.load(todo_file)
    except FileNotFoundError:
        init_guild_todos(guild_id)
    except json.JSONDecodeError:
        init_guild_todos(guild_id, True)
    return get_guild_todos(guild_id)


def init_guild_todos(guild_id: int, force_init=False):
    if not os.path.exists(f"data/servers/{guild_id}/"):
        os.makedirs(f"data/servers/{guild_id}/")
    if (not os.path.exists(f"data/servers/{guild_id}/todo.json")) or force_init:
        json.dump([], open(f"data/servers/{guild_id}/todo.json", "w+"))


def rm_guild_todo(guild_id: int, index: int):
    todo_data = get_guild_todos(guild_id)
    try:
        todo_data.pop(index)
    except IndexError:
        raise IndexError(f"Index {index} does not exist in to-do data for guild {guild_id}")
    if len(todo_data) == 0:
        os.remove(f"data/servers/{guild_id}/todo.json")
    else:
        with open(f"data/servers/{guild_id}/todo.json", "w+", newline="\n", encoding='utf-8') \
                as todo_file:
            json.dump(todo_data, todo_file)
            todo_file.close()
    return


def add_guild_todo(guild_id: int, description: str, author_id: int):
    todo_data = get_guild_todos(guild_id)
    new_todo = {
        'desc': description,
        'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        'author': author_id
    }
    todo_data.append(new_todo)
    with open(f"data/servers/{guild_id}/todo.json", 'w+', newline="\n", encoding='utf-8') as \
            todo_file:
        json.dump(todo_data, todo_file)
        todo_file.close()
