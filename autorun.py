#!/usr/bin/env python3

import os

if os.name != "posix":
    exit("This script does not seem to be running on Posix, the OS it was designed for.")

import subprocess
import time
import sys
import json
import shutil

try:
    import requests
except ImportError:
    print("requests not installed, using pip to install it.")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'requests'], shell=False)
    print("requests installed and imported")
    import requests

try:
    import git
except ImportError:
    print("git-python not installed, using pip to install it.")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'git-python'], shell=False)
    print("git-python installed")
    import git

try:
    from config import *
except ImportError:
    raise ImportError("Uh, you may want to create a config file for this script?")

pip_cmd = [sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt']


def drop_clone(git_path):
    if not os.path.exists(git_path):
        os.mkdir(git_path)
    elif os.path.exists(f'{git_path}/drop-bot/'):
        shutil.rmtree(f'{git_path}/drop-bot/')
    local_git = git.Git(git_path)
    local_git.clone(gitHubRepo)
    shutil.rmtree(f'{git_path}/drop-bot/.git/')
    shutil.rmtree(f'{git_path}/drop-bot/.github/')  # clears out unnecessary folders
    shutil.rmtree(f'{git_path}/drop-bot/.vscode/')


runs = 0
newJson = requests.get(confJsonUrl).json()


def check_config(conf: str):
    newconf = json.load(open(conf))
    for key, value in newconf.items():
        if newJson.get(key):
            if not isinstance(value, type(newJson[key])):
                newconf[key] = newJson[key]
    for key, value in newJson.items():
        if not newconf.get(key):
            newconf[key] = value
    if useDevToken:
        newconf['dev_token'] = True
    if customBotDesc:
        newconf['bot_description'] = customBotDesc
    else:
        newconf['bot_description'] = newJson['bot_description']
    if rawTermOutput:
        newconf['clear_terminal'] = False
        newconf['change_terminal_name'] = False
    if useSteamRecentlyPlayed != 0:
        newconf['useSteamRecentlyPlayed'] = int(useSteamRecentlyPlayed)
        steam_api_conf = newconf['steamApi']
        steam_api_conf['userId'] = steamUserId
        steam_api_conf['key'] = steamApiKey
        steam_api_conf['excludedGames'] = excludedGames
    newconf['owner_id'] = ownerId
    newconf['verbose'] = verbose
    newconf['syncActivityWithOwner'] = syncOwnerActivity
    return newconf


prevDropJson = None
if doSubdirectoryCleanup:
    previousDropDirs = []
    for directory in [directory.path for directory in os.scandir(os.getcwd()) if directory.is_dir()]:
        if str(directory.split('/')[-1]).startswith('drop-bot'):
            previousDropDirs.append(directory)
        else:
            shutil.rmtree(directory)
    previousDropDirs.reverse()
    if previousDropDirs:
        for directory in previousDropDirs:
            if os.path.isfile(f'{directory}/drop-bot/data/config.json'):
                prevDropJson = check_config(f'{directory}/drop-bot/data/config.json')
                if doTransferServerData:
                    if os.path.isdir('.temp/'):
                        shutil.rmtree('.temp/')
                    os.mkdir('.temp/')
                    os.mkdir('.temp/data/')
                    if os.path.isdir(f'{directory}/drop-bot/data/servers/'):
                        shutil.move(f'{directory}/drop-bot/data/servers/', '.temp/data/')
                    if os.path.isfile(f'{directory}/drop-bot/data/data_clear.json'):
                        shutil.move(f'{directory}/drop-bot/data/data_clear.json', '.temp/data/data_clear.json')
                    if os.path.isfile(f'{directory}/drop-bot/data/unmutes.json'):
                        shutil.move(f'{directory}/drop-bot/data/unmutes.json', '.temp/data/unmutes.json')
                shutil.rmtree(directory)
                break
            else:
                shutil.rmtree(directory)

print(f"Cloning repository to drop-bot{runs + 1}/")
drop_clone(f'drop-bot{runs + 1}')

if doPipInstallReqs:
    reqs = requests.get(reqsTxtUrl).text
    if not os.path.isfile('requirements.txt') or open('requirements.txt').read() != reqs:
        print(f'Running {str(pip_cmd)}')
        open('requirements.txt', 'w').write(reqs)
        try:
            subprocess.check_call(pip_cmd, shell=False)
        except subprocess.CalledProcessError:
            exit("Uh oh, seems like something didn't go right while trying to install the bot's requirements. "
                 "Troubleshooting or manual installation required. I'm aborting now.")

while True:
    if os.path.exists(f'drop-bot{runs}'):
        shutil.rmtree(f'drop-bot{runs}')
    runs = runs + 1
    bot_cmd = [sys.executable, 'main.py']

    if prevDropJson:
        json.dump(prevDropJson, open(f'drop-bot{runs}/drop-bot/data/config.json', 'w'))
    if autoWriteTokens:
        open(f'drop-bot{runs}/drop-bot/data/token.txt', 'w').write(token)
        open(f'drop-bot{runs}/drop-bot/data/devtoken.txt', 'w').write(devToken)
    if os.path.isdir('.temp/'):
        root_src_dir = '.temp/'
        root_dst_dir = f'drop-bot{runs}/drop-bot/'
        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)
            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)
            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)
                if os.path.exists(dst_file):
                    # in case of the src and dst are the same file
                    if os.path.samefile(src_file, dst_file):
                        continue
                    os.remove(dst_file)
                shutil.copy(src_file, dst_dir)
        shutil.rmtree('.temp/')

    print(f'Running loop, take {runs}')
    sp = subprocess.Popen(bot_cmd, shell=False, cwd=f'drop-bot{runs}/drop-bot/')

    try:
        time.sleep(runtime)
    except KeyboardInterrupt:
        exit("KeyboardInterrupt, aborting.")

    # Due for an update. Do stuff, I guess.
    drop_clone(f'drop-bot{runs + 1}')
    newJson = json.load(open(f'drop-bot{runs + 1}/drop-bot/data/config.json'))
    json.dump(check_config(f'drop-bot{runs}/drop-bot/data/config.json'),
              open(f'drop-bot{runs + 1}/drop-bot/data/config.json', 'w'))
    if autoWriteTokens:
        open(f'drop-bot{runs + 1}/drop-bot/data/token.txt', 'w').write(token)
        open(f'drop-bot{runs + 1}/drop-bot/data/devtoken.txt', 'w').write(devToken)
    if doTransferServerData:
        if os.path.isdir('.temp/'):
            shutil.rmtree('.temp/')
        os.mkdir('.temp/')
        os.mkdir('.temp/data/')
        if os.path.isdir(f'drop-bot{runs}/drop-bot/data/servers/'):
            shutil.move(f'drop-bot{runs}/drop-bot/data/servers/', f'drop-bot{runs + 1}/drop-bot/data/')
        if os.path.isfile(f'drop-bot{runs}/drop-bot/data/data_clear.json'):
            shutil.copy(f'drop-bot{runs}/drop-bot/data/data_clear.json',
                        f'drop-bot{runs + 1}/drop-bot/data/data_clear.json')
        if os.path.isfile(f'drop-bot{runs}/drop-bot/data/unmutes.json'):
            shutil.move(f'drop-bot{runs}/drop-bot/data/unmutes.json',
                        f'drop-bot{runs + 1}/drop-bot/data/unmutes.json')
    if doPipInstallReqs:
        reqs = requests.get(reqsTxtUrl).text
        if not os.path.isfile('requirements.txt') or open('requirements.txt').read() != reqs:
            print(f'Running {str(pip_cmd)}')
            open('requirements.txt', 'w').write(reqs)
            try:
                subprocess.check_call(pip_cmd, shell=False)
            except subprocess.CalledProcessError:
                exit("Uh oh, seems like something didn't go right while trying to install the bot's requirements. "
                     "Troubleshooting or manual installation required. I'm aborting now.")

    sp.terminate()
    sp.kill()
