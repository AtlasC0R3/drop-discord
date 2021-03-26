#!/usr/bin/env python3
import os
import io
import datetime
import json
import time
import sys
from datetime import datetime
import random
import ast

if os.getcwd().lower().startswith('c:\\windows\\system32'):  # Windows is confusing to work with.
    # What is this place?!
    print("Uh, the program is running under Windows' System32 directory, which can cause problems.\n"
          "One of these problems being the fact that it will not be able to access its configuration files,\n"
          "and the fact that it may also create redundant files in the System32 directory.\nThis problem can be caused "
          "in many ways: you may have tried running this bot using the 'Quick access' page.\n"
          "Anyhow, I'm aborting now.\n\n")  # two newlines. yes.
    os.system('pause')
    exit(1)

# External libraries that need to be imported
from data.extdata import TermColors, get_config_parameter, get_server_config, write_server_config, get_github_config, \
    get_language_str, get_new_activity

from drop.basic import init_genius

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

try:
    from drop import moderation, mute
except ImportError:
    sys.exit("drop-mod has not been installed. "
             "This bot requires it to have help commands (which are required). "
             "Please install it using:\n  pip install drop-mod\n"
             "or by running\n  pip install -r requirements.txt")

verbose = get_config_parameter('verbose', bool)
clear_terminal = get_config_parameter('clear_terminal', bool)
change_terminal_name = get_config_parameter('change_terminal_name', bool)

cogs = []
for cog_file in os.listdir('cogs/'):
    if cog_file.endswith('.py'):
        cog_import = 'cogs.' + cog_file.split('.')[0]
        cogs.append(cog_import)
        if verbose:
            print(f'Found {cog_file} as cog')


def get_prefix(client, message):
    if message.guild:
        prefixes = get_server_config(message.guild.id, 'prefix', str)
    else:
        prefixes = ['', '!']
    # If the message was sent in a guild, get the guild's prefix. Else, just put either no prefix or the '!' prefix.

    # Allow users to @mention the bot instead of using a prefix when using a command. Also optional
    # Do `return prefixes` if you don't want to allow mentions instead of prefix.
    return commands.when_mentioned_or(*prefixes)(client, message)
    # thanks EvieePy for this snippet of code.


intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.presences = True
# F**k intents.

bot = commands.Bot(  # Create a new bot
    command_prefix=get_prefix,  # Set the prefix
    description=get_config_parameter('bot_description', str),  # Set a description for the bot
    owner_id=get_config_parameter('owner_id', int),  # Your unique User ID
    case_insensitive=True,  # Make the commands case insensitive
    intents=intents,  # I think I made intents
    help_command=PrettyHelp()  # Sets custom help command to discord_pretty_help's
)

ownerMember = None
ownerUser = None
ownerId = get_config_parameter('owner_id', int)
bot_mention = None


@bot.event
async def on_ready():
    if verbose:
        print('Bot is ready: everything should have loaded successfully.')
    else:
        if os.name == 'nt':
            if clear_terminal:
                os.system("cls")
            if change_terminal_name:
                os.system(f"title {bot.user}")
        elif os.name == 'posix':
            if clear_terminal:
                os.system("clear")
            if change_terminal_name:
                os.system(f"printf '\\033]2;{bot.user}\\a'")  # Sets terminal name to the bot's user.
        else:
            # What the hell is this running on!?
            print(f"Running on an unknown OS ({os.name})")
    get_github_config()
    print(f'My name is {bot.user}.')

    try:
        if ownerId:
            owner_refresh.start()
        activity_changer.start()
        inactivity_func.start()
    except RuntimeError:
        # whoops, already started.
        pass

    for cog in cogs:
        if verbose:
            print(f'Loading {cog}')
        try:
            bot.load_extension(cog)
        except discord.ext.commands.errors.ExtensionAlreadyLoaded:
            # Bot tried to load a cog that was already loaded.
            print(f"{TermColors.WARNING}WARN: Tried to load a cog/extension that was already loaded "
                  f"({cog}).{TermColors.ENDC}")
    if get_config_parameter('geniusApi', str):
        init_genius(get_config_parameter('geniusApi', str))

    global bot_mention
    bot_mention = f'<@!{bot.user.id}>'
    return


if verbose:
    print('on_ready has been configured')

message_count = {}


@bot.check
async def command_check(ctx):
    if not ctx.guild:
        return True
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
    if message.guild:
        # if (not message.author.guild_permissions.manage_messages) or \
        #         (not message.author.guild_permissions.manage_guild):
        if True:
            for item in get_server_config(message.guild.id, 'no_no_words', dict):
                if item in message.content.lower().replace(" ", ""):
                    try:
                        await message.delete()
                        penalties = get_server_config(message.guild.id, 'no_no_words', dict)
                        if penalties.get(item):
                            penalties = penalties.get(item)
                            if "ban" in penalties:
                                await message.author.ban(reason=f'Banned for saying word {item}\n'
                                                                f'Full message: {message.content}')
                            elif "kick" in penalties:
                                await message.author.kick(reason=f'Kicked for saying word {item}\n'
                                                                 f'Full message: {message.content}')
                            elif "mute" in penalties:
                                role = message.guild.get_role(get_server_config(message.guild.id, 'mute_role', int))
                                await message.author.add_roles(role)
                                mute.add_mutes(message.guild.id, role.id, message.author.id, bot.user.id, "1 hour")
                            if "warn" in penalties:
                                moderation.warn(message.guild.id, message.author.id, message.author.name,
                                                bot.user.id, bot.user.name, message.channel.id,
                                                f'Warned for saying word {item}\n'
                                                f'Full message: {message.content}')
                    except discord.errors.Forbidden:
                        await message.channel.send(get_language_str(message.guild.id, 5))
                    # People expect the bot to work without even giving them the perms.
    if message.author.id == bot.user.id:
        return  # To prevent the bot itself from triggering things.
    global message_count
    if message.guild and get_server_config(message.guild.id, 'inactivity_func', bool) and \
            message.channel.id in get_server_config(message.guild.id, 'inactivity_channels', list):
        if message.channel.id in message_count:
            count = message_count[message.channel.id]
        else:
            count = 0
        message_count[message.channel.id] = count + 1
    if message.content == bot_mention:
        if message.author.id in get_server_config(message.guild.id, 'asked_prefix', list):
            lang = get_server_config(message.guild.id, 'language', str)
            to_send = get_language_str(lang, 0)
            await message.channel.send(random.choice(to_send).format(message))
            return
        else:
            lang = get_server_config(message.guild.id, 'language', str)
            to_send = get_language_str(lang, 4)
            await message.channel.send(to_send.format(get_server_config(message.guild.id, 'prefix', str)))
            asked = get_server_config(message.guild.id, 'asked_prefix', list)
            asked.append(message.author.id)
            write_server_config(message.guild.id, 'asked_prefix', asked)
    if '(╯°□°）╯︵ ┻━┻' in message.content and message.guild:
        if get_server_config(message.guild.id, 'tableflip', bool):
            time.sleep(0.75)
            lang = get_server_config(message.guild.id, 'language', str)
            to_send = get_language_str(lang, 2)
            to_send = random.choice(to_send)
            await message.channel.send(to_send.format(message))

    if message.content.startswith(f'{bot_mention} activity') and message.author.id == ownerId:
        with open("data/activities.json", encoding='utf-8', newline="\n") as f:
            activities = json.load(f)
        if " activity " in message.content:
            activity = message.content.replace(f'{bot_mention} activity ', '')
            # user passed arguments
        else:
            activity = None
        activity_type = None
        activity_name = None
        if activity:
            if activity.startswith('[') or activity.isdigit():
                activity_entry = ast.literal_eval(activity)
                if type(activity_entry) is int:
                    try:
                        activity = activities[activity_entry]
                    except IndexError:
                        await message.channel.send("Wrong activity! **>:(**")
                        return
                    activity_type = activity[0]
                    activity_name = activity[1]
                    await message.channel.send(content=f'{activity_type.title()} {activity_name}, is this correct?')

                    def check(ms):
                        return ms.channel == message.channel and ms.author == message.author

                    reply_msg = await bot.wait_for('message', check=check)
                    reply_from_user = reply_msg.content.lower()

                    if reply_from_user in ('y', 'yes', 'confirm'):
                        pass
                    else:
                        return
                elif type(activity_entry) is list:
                    try:
                        activity_type = activity_entry[0]
                        activity_name = activity_entry[1]
                        await bot.change_presence(
                            activity=discord.Activity(type=discord.ActivityType[activity_type], name=activity_name))
                    except (KeyError, IndexError):
                        await message.channel.send("Invalid list! Here's an example of how an activity list should be:"
                                                   "\n"
                                                   f"```{random.choice(activities)}```")
                        return
            else:
                activity_list = activity.split(' ')
                if activity_list[0] in [x.name for x in discord.ActivityType]:
                    activity_type = activity_list[0]
                    activity_name = " ".join(activity_list[1:])
                else:
                    activity_type = 'playing'
                    activity_name = activity
        else:
            activity = get_new_activity(message.author)
            activity_type = activity[0]
            activity_name = activity[1]
        await bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType[activity_type], name=activity_name))
        await message.reply(content=f'{activity_type.title()} {activity_name}')


if verbose:
    print('on_message has been configured')


@tasks.loop(minutes=2, count=None, reconnect=True)
async def owner_refresh():
    if verbose:
        print("Refreshing owner member and user objects")
    global ownerUser
    ownerUser = bot.get_user(ownerId)
    for member in bot.get_all_members():
        if member.id == ownerId:
            global ownerMember
            ownerMember = member


@tasks.loop(minutes=10, count=None, reconnect=True)
async def activity_changer():
    if ownerMember:
        activity = get_new_activity(ownerMember)
    else:
        activity = get_new_activity()
    activity_type = activity[0]
    activity_name = activity[1]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType[activity_type], name=activity_name))


@tasks.loop(minutes=5)
async def inactivity_func():
    global message_count
    for x in message_count:
        if message_count[x] in range(2, 10):
            with open("data/quotes/inactivity_quotes.json", encoding='utf-8', newline='\n') as f:
                inactivity_quotes = json.load(f)
            channel = bot.get_channel(int(x))
            await channel.send(random.choice(inactivity_quotes))
    message_count = {}


if verbose:
    print('Task loops has been configured')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandInvokeError):
        if isinstance(error.original, discord.Forbidden):
            await ctx.reply(get_language_str(get_server_config(ctx.guild.id, 'language', str), 6))
            return
    if not isinstance(error, (commands.CommandNotFound, commands.MissingPermissions, commands.MissingRequiredArgument,
                              commands.DisabledCommand, commands.CheckFailure, commands.MemberNotFound)):
        if ctx.author.id == bot.owner_id:
            try:
                await ctx.reply(str(error))
            except discord.errors.HTTPException:
                pass  # probably unknown message, who knows.
        elif get_server_config(ctx.guild.id, 'share_error_logs', bool):
            dt_string = datetime.now().strftime("%d_%m_%Y %H %M %S")
            if not os.path.exists(f"data/errors/{type(error).__name__}/"):
                os.makedirs(f"data/errors/{type(error).__name__}/")
            open(f"data/errors/{type(error).__name__}/error_{dt_string}.txt", "w+", encoding="utf-8",
                 newline="\n").write(
                f"[{error}] while trying to invoke [{ctx.message.content}]")
        else:
            error_file = io.BytesIO(bytes(str(error), 'utf-8'))
            await ctx.reply(content=get_language_str(get_server_config(ctx.guild.id, 'language', str), 8),
                            file=discord.File(error_file, 'error.txt'))


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
            with open("data/data_clear.json", "w", encoding="utf-8", newline="\n") as d_clear:
                json.dump(data_clear, d_clear, indent=2)


if get_config_parameter('dev_token', bool):
    print("WARN: Developer mode activated, passing through developer token.")
    try:
        print("Trying to load Jishaku")
        bot.load_extension('jishaku')
    except discord.ext.commands.errors.ExtensionNotFound:
        print("Could not load Jishaku: skipping...")
    else:
        print("Jishaku loaded: continuing...")
    token_path = "data/devtoken.txt"
else:
    if verbose:
        print('Using regular token')
    token_path = "data/token.txt"

try:
    specified_token = open(token_path, "rt").read()
except FileNotFoundError:
    specified_token = input("Seems like I couldn't find the token, please enter it: ")
    reply = input("Got it. Would you like to save that token for future use cases? (y/n)\n").lower()
    if reply in ('y', 'yes'):
        open(token_path, "w+", newline="\n", encoding='utf-8').write(specified_token)
        print("Alright, token saved. Running bot...\n")
    elif reply in ('n', 'no'):
        print("Alright, running bot.\n")
    else:
        print("I didn't quite get that... I'll take that as a no.\n")

if verbose:
    print('Connecting to Discord...')
bot.run(specified_token, bot=True, reconnect=True)
