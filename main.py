import ast
import io
import datetime
import json
import os
import time
import sys
from datetime import datetime
import random

from data.classes import bcolors
from data.classes import get_config_parameter
from data.classes import get_server_config
from data.classes import write_server_config

# External libraries that need to be imported
try:
    import discord
except ImportError:
    sys.exit("Discord.py has not been installed, or at least I failed to load it. This Python app requires it. "
             "Please install it using:\n  pip install discord.py\n"
             "or by running\n  pip install -r requirements.txt")
from discord.ext import commands, tasks

try:
    from pretty_help import PrettyHelp
except ImportError:
    sys.exit("discord-pretty-help has not been installed. "
             "This bot requires it to have help commands (which are required). "
             "Please install it using:\n  pip install discord-pretty-help\n"
             "or by running\n  pip install -r requirements.txt")

cogs = []
for cogfile in list(os.listdir('cogs/')):
    if cogfile.endswith('.py'):
        cogimport = 'cogs.' + cogfile.split('.')[0]
        cogs.append(cogimport)


def get_prefix(client, message):
    if message.guild:
        prefixes = get_server_config(message.guild.id, 'prefix', str)
    else:
        prefixes = ['', '!']
    # If the message was sent in a guild, get the guild's prefix. Else, just put either no prefix or the '!' prefix.

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if you don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)
    # thanks evieepy for this snippet of code.


intents = discord.Intents.default()
intents.members = True
# F**k intents.

bot = commands.Bot(  # Create a new bot
    command_prefix=get_prefix,  # Set the prefix
    description=get_config_parameter('bot_description', str),  # Set a description for the bot
    owner_id=get_config_parameter('owner_id', int),  # Your unique User ID
    case_insensitive=True,  # Make the commands case insensitive
    intents=intents,  # I think I made intents
    help_command=PrettyHelp()  # Sets custom help command to discord_pretty_help's
)


@bot.event
async def on_ready():
    if os.name == 'nt':
        os.system("cls")
        os.system(f"title {bot.user}")
        print(f"Running on Windows ({os.name})")
    elif os.name == "darwin":
        print(f"Running on macOS ({os.name})")
    elif os.name == 'posix':
        os.system("clear")
        os.system(f"printf '\\033]2;{bot.user}\\a'")  # Sets terminal name to the bot's user.
        print(f"Running on Posix/Linux ({os.name})")
    else:
        # What the hell is this running on!?
        print(f"Running on an unknown OS ({os.name})")
    print(f'My name is {bot.user}.')
    try:
        for cog in cogs:
            bot.load_extension(cog)
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        # Bot tried to load a cog that was already loaded.
        print(f"{bcolors.WARNING}WARN: Tried to load a cog/extension that was already loaded.{bcolors.ENDC}")
        return
    activitychanger.start()
    temp_undo.start()
    inactivity_func.start()
    return


messagecount = {}


@bot.check
async def command_check(ctx):
    disabled_commands = get_server_config(ctx.guild.id, 'disabled_commands', list)
    return str(ctx.command) not in disabled_commands


@bot.listen()
async def on_message(message):
    for item in get_server_config(message.guild.id, 'no_no_words', list):
        if item in message.content.lower():
            try:
                await message.delete()
            except discord.errors.Forbidden:
                await message.channel.send("Hey, you said something you were not supposed to say! "
                                           "Unfortunately for me (and probably fortunately for you), "
                                           "I don't have the permissions to delete your message.")
                # People expect the bot to work without even giving them the perms.
    if message.author.id == bot.user.id:
        return  # To prevent the bot itself from triggering things.
    global messagecount
    if message.guild and get_server_config(message.guild.id, 'inactivity_func', bool) and \
            message.channel.id in get_server_config(message.guild.id, 'inactivity_channels', list):
        if message.channel.id in messagecount:
            count = messagecount[message.channel.id]
        else:
            count = 0
        messagecount[message.channel.id] = count + 1
    bot_mention = f'<@!{bot.user.id}>'
    if message.content == bot_mention:
        if message.author.id in get_server_config(message.guild.id, 'asked_prefix', list):
            with open("data/quotes/salutes.json", encoding='utf-8', newline="\n") as f:
                data = json.load(f)
            await message.channel.send(random.choice(data).format(message))
            return
        else:
            await message.channel.send(f"My prefix here is `{get_server_config(message.guild.id, 'prefix', str)}`.")
            asked = get_server_config(message.guild.id, 'asked_prefix', list)
            asked.append(message.author.id)
            write_server_config(message.guild.id, 'asked_prefix', asked)
    if '(╯°□°）╯︵ ┻━┻' in message.content:
        time.sleep(0.75)
        messages = json.load(open("data/quotes/tableflip.json", "r", encoding="utf-8", newline="\n"))
        to_send = random.choice(messages)
        await message.channel.send(to_send.format(message))


@tasks.loop(minutes=10, count=None, reconnect=True)
async def activitychanger():
    with open("data/activities.json", encoding='utf-8', newline="\n") as f:
        dictionary = json.load(f)
    activity = random.choice(dictionary)
    activitytype = activity[0]
    activityname = activity[1]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType[activitytype], name=activityname))


@tasks.loop(minutes=5)
async def inactivity_func():
    global messagecount
    for x in messagecount:
        if messagecount[x] in range(2, 10):
            with open("data/quotes/inactivity_quotes.json", encoding='utf-8', newline='\n') as f:
                inactivities = json.load(f)
            channel = bot.get_channel(int(x))
            await channel.send(random.choice(inactivities))
    messagecount = {}


@bot.event
async def on_command_error(ctx, error):
    if not isinstance(error, (commands.CommandNotFound, commands.MissingPermissions, commands.MissingRequiredArgument,
                              commands.DisabledCommand, commands.CheckFailure)):
        if get_config_parameter('save_errors', bool):
            dt_string = datetime.now().strftime("%d_%m_%Y %H %M %S")
            if not os.path.exists(f"data/errors/{type(error).__name__}/"):
                os.makedirs(f"data/errors/{type(error).__name__}/")
            open(f"data/errors/{type(error).__name__}/error_{dt_string}.txt", "w+", encoding="utf-8",
                 newline="\n").write(
                f"[{error}] while trying to invoke [{ctx.message.content}]")
        else:
            errorio = io.BytesIO(bytes(str(error), 'utf-8'))
            await ctx.send(content="Uh oh! I ran into an error.\n"
                                   "Because this server's configuration doesn't allow me to automatically save errors, "
                                   "you'll have to do it yourself.",
                           file=discord.File(errorio, 'error.txt'))


@tasks.loop(minutes=30)
async def temp_undo():
    dt_string = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data/temp_penalties.json", "r", encoding="utf-8", newline="\n") as f:
        data = json.load(f)
    if dt_string in data:
        guilds = []
        users = []
        for x in data.get(dt_string):
            guild_id = x[2]
            guild = bot.get_guild(guild_id)
            role_id = x[1]
            role = discord.utils.get(guild.roles, id=role_id)
            user_id = x[0]
            user_member = guild.get_member(user_id)  # holy s*** i need to learn intents.
            await user_member.remove_roles(role)
            x.pop()
            guilds.append(guild_id)
            users.append(user_id)
        # stuff done, now we just have to delete residue *correctly*.

        with open("data/temp_penalties.json", "r+", encoding='utf-8', newline="\n") as tempf:
            data = json.load(tempf)
            data.pop(dt_string)
            for x in users:
                for y in guilds:
                    try:
                        data[str(y)].pop(str(x))
                    except KeyError:
                        pass  # Wrong guild/user combination.
                    if not data.get(str(y)):
                        data.pop(str(y))

            tempf.seek(0)
            json.dump(data, tempf, indent=2)
            tempf.truncate()
            # wwwwww... How does all of this work..? It.. does?!
            # I'm amazed and confused at the same time.


try:
    specified_token = open("data/token.txt", "rt").read()
except FileNotFoundError:
    specified_token = input("Seems like I couldn't find the token, please enter it: ")
    reply = input("Got it. Would you like to save that token for future use cases? (y/n)\n").lower()
    if reply in ('y', 'yes'):
        open("data/token.txt", "w+", newline="\n", encoding='utf-8').write(specified_token)
        print("Alright, token saved. Running bot...\n")
    elif reply in ('n', 'no'):
        print("Alright, running bot.\n")
    else:
        print("I didn't quite get that... I'll take that as a no.\n")

bot.run(specified_token, bot=True, reconnect=True)
