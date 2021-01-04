import os
import io
import datetime
import json
import time
import sys
from datetime import datetime
import random
import shutil

from data.classes import TermColors
from data.classes import get_config_parameter
from data.classes import get_server_config
from data.classes import write_server_config
from data.classes import get_github_config
from data.classes import get_steam_played_game

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
for cogfile in os.listdir('cogs/'):
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
intents.guilds = True

bot = commands.Bot(                                            # Create a new bot
    command_prefix=get_prefix,                                 # Set the prefix
    description=get_config_parameter('bot_description', str),  # Set a description for the bot
    owner_id=get_config_parameter('owner_id', int),            # Your unique User ID
    case_insensitive=True,                                     # Make the commands case insensitive
    intents=intents,                                           # I think I made intents
    help_command=PrettyHelp()                                  # Sets custom help command to discord_pretty_help's
)


@bot.event
async def on_ready():
    get_github_config()
    if os.name == 'nt':
        if get_config_parameter('clear_terminal', bool):
            os.system("cls")
        if get_config_parameter('change_terminal_name', bool):
            os.system(f"title {bot.user}")
        print(f"Running on Windows ({os.name})")
    elif os.name == "darwin":
        print(f"Running on macOS ({os.name})")
    elif os.name == 'posix':
        if get_config_parameter('clear_terminal', bool):
            os.system("clear")
        if get_config_parameter('change_terminal_name', bool):
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
        print(f"{TermColors.WARNING}WARN: Tried to load a cog/extension that was already loaded.{TermColors.ENDC}")
        return
    activitychanger.start()
    temp_undo.start()
    inactivity_func.start()
    return


messagecount = {}


@bot.check
async def command_check(ctx):
    disabled_commands = get_server_config(ctx.guild.id, 'disabled_commands', list)
    disabled_cogs = get_server_config(ctx.guild.id, 'disabled_cogs', list)
    cog_disabled = False
    if ctx.command.cog:
        cog_disabled = ctx.command.cog.qualified_name in disabled_cogs
    command_disabled = str(ctx.command) in disabled_commands
    is_disabled = True
    if cog_disabled:
        is_disabled = False
    elif command_disabled:
        is_disabled = False
    return is_disabled  # What a mess.


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
    if get_config_parameter('useSteamRecentlyPlayed', bool):
        activitytype = 'playing'
        activityname = get_steam_played_game()
    else:
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
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            await ctx.send("Sorry, I do not have the permissions to do that.")
            return
    if not isinstance(error, (commands.CommandNotFound, commands.MissingPermissions, commands.MissingRequiredArgument,
                              commands.DisabledCommand, commands.CheckFailure, commands.MemberNotFound)):
        if get_server_config(ctx.guild.id, 'share_error_logs', bool):
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


@bot.event
async def on_guild_join(guild):
    with open("data/data_clear.json", "r", encoding="utf-8", newline="\n") as f:
        data_clear = json.load(f)
        if str(guild.id) in data_clear:
            # Data deletion has been queued, but will need to be cancelled.
            system_channel = guild.system_channel
            if system_channel:
                await system_channel.send("Woah there. It seems like this server had their data deletion queued. "
                                          "Since someone invited me back, this data deletion queue will be cancelled. "
                                          "If you'd like to queue it back, please run the `cleardata` command again "
                                          "(and don't invite me back in this server).")
            else:
                # No channel has been set for system messages. So, just say no warning, I guess...
                pass
            guild_entry = data_clear[str(guild.id)]
            data_clear[guild_entry[0]].pop(guild_entry[1])
            data_clear.pop(str(guild.id))
            if not data_clear[guild_entry[0]]:
                data_clear.pop(guild_entry[0])
            with open("data/data_clear.json", "w", encoding="utf-8", newline="\n") as dclear:
                json.dump(data_clear, dclear, indent=2)


@tasks.loop(minutes=1)
async def temp_undo():
    dt_string = datetime.now().strftime("%Y-%m-%d %H:%M")
    with open("data/unmutes.json", "r", encoding="utf-8", newline="\n") as f:
        unmutes = json.load(f)
    with open("data/data_clear.json", "r", encoding="utf-8", newline="\n") as f:
        data_clear = json.load(f)
    if dt_string in unmutes:
        guilds = []
        users = []
        for toUnmute in unmutes.get(dt_string):
            guild_id = toUnmute[2]
            guild = bot.get_guild(guild_id)
            role_id = toUnmute[1]
            role = discord.utils.get(guild.roles, id=role_id)
            user_id = toUnmute[0]
            user_member = guild.get_member(user_id)  # holy s*** i need to learn intents.
            await user_member.remove_roles(role)
            toUnmute.pop()
            guilds.append(guild_id)
            users.append(user_id)
        # Stuff done, remove leftovers
        with open("data/unmutes.json", "r+", encoding='utf-8', newline="\n") as unmuteFile:
            unmutes = json.load(unmuteFile)
            unmutes.pop(dt_string)
            for toUnmute in users:
                for y in guilds:
                    try:
                        unmutes[str(y)].pop(str(toUnmute))
                    except KeyError:
                        pass  # Wrong guild/user combination.
                    if not unmutes.get(str(y)):
                        unmutes.pop(str(y))
            unmuteFile.seek(0)
            json.dump(unmutes, unmuteFile, indent=2)
            unmuteFile.truncate()
    if dt_string in data_clear:
        guilds = []
        now_clears = data_clear.get(dt_string)
        for toClear in now_clears:
            guild_id = toClear
            try:
                shutil.rmtree(f'data/servers/{guild_id}/')
            except OSError:
                pass  # Directory already removed (???)
            guilds.append(guild_id)
            now_clears = [x for x in now_clears if x != toClear]
        # Stuff done, remove leftovers 2: electric boogaloo
        with open("data/data_clear.json", "r+", encoding='utf-8', newline="\n") as data_clear_json:
            data_clears = json.load(data_clear_json)
            data_clears.pop(dt_string)
            for toPop in guilds:
                data_clears.pop(str(toPop))
            data_clear_json.seek(0)
            json.dump(data_clears, data_clear_json, indent=2)
            data_clear_json.truncate()


if get_config_parameter('dev_token', bool):
    print("WARN: Developer mode activated, passing through developer token.")
    tokenpath = "data/devtoken.txt"
else:
    tokenpath = "data/token.txt"

try:
    specified_token = open(tokenpath, "rt").read()
except FileNotFoundError:
    specified_token = input("Seems like I couldn't find the token, please enter it: ")
    reply = input("Got it. Would you like to save that token for future use cases? (y/n)\n").lower()
    if reply in ('y', 'yes'):
        open(tokenpath, "w+", newline="\n", encoding='utf-8').write(specified_token)
        print("Alright, token saved. Running bot...\n")
    elif reply in ('n', 'no'):
        print("Alright, running bot.\n")
    else:
        print("I didn't quite get that... I'll take that as a no.\n")

bot.run(specified_token, bot=True, reconnect=True)
