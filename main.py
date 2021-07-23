#!/usr/bin/env python3
import os
import io
import datetime
import json
import asyncio
import sys
from datetime import datetime
import random
import logging

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
from data.extdata import get_config_parameter, get_server_config, write_server_config, get_github_config, \
    get_language_str, get_new_activity, check_banword_filter, get_listening_to

from drop.basic import init_genius
from drop.tempban import check_bans

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
             "That's basically this bot's backend. "
             "Please install it using:\n  pip install drop-mod\n"
             "or by running\n  pip install -r requirements.txt")

if get_config_parameter('slash_commands', bool):
    try:
        from discord_slash import SlashCommand
    except ImportError:
        sys.exit("discord-py-slash-command has not been installed, even though "
                 "slash commands are enabled in the bot's config.json file. "
                 "To use slash commands, please install the slash-command library using:\n  "
                 "pip install discord-py-slash-command\n")
from discord_components import DiscordComponents

verbose = get_config_parameter('verbose', bool)
clear_terminal = get_config_parameter('clear_terminal', bool)
change_terminal_name = get_config_parameter('change_terminal_name', bool)

if verbose:
    logging.basicConfig(level=logging.INFO)
else:
    logging.basicConfig(level=logging.WARNING)

cogs = []
for cog_file in os.listdir('cogs/'):
    if cog_file.endswith('.py') and cog_file != 'slash.py':
        cog_import = 'cogs.' + cog_file.split('.')[0]
        cogs.append(cog_import)
        logging.info(f'Found {cog_file} as cog')

if get_config_parameter('slash_commands', bool):
    cogs.append('cogs.slash')


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


intents = discord.Intents.all()
# F**k intents.

bot = commands.Bot(                                            # Create a new bot
    command_prefix=get_prefix,                                 # Set the prefix
    description=get_config_parameter('bot_description', str),  # Set a description for the bot
    owner_id=get_config_parameter('owner_id', int),            # Your unique User ID
    case_insensitive=True,                                     # Make the commands case insensitive
    intents=intents,                                           # I think I made intents
    help_command=PrettyHelp()                                 # Sets custom help command to discord_pretty_help's
)
if get_config_parameter('slash_commands', bool):
    bot.slash = SlashCommand(bot, override_type=True, sync_commands=True, sync_on_cog_reload=True)

bot.listening_activities = []  # Sets the list for listening activities

ownerMember = None
ownerUser = None
ownerId = get_config_parameter('owner_id', int)
bot_mention = None
bot_mention_mobile = None

for cog in cogs:
    logging.info(f'Loading {cog}')
    try:
        bot.load_extension(cog)
    except discord.ext.commands.errors.ExtensionAlreadyLoaded:
        # Bot tried to load a cog that was already loaded.
        logging.warning(f"Tried to load a cog/extension that was already loaded ({cog})")


async def check_message(message):
    result = check_banword_filter(message.content, message.guild.id)
    penalty = result[0]
    if penalty != 0:
        try:
            await message.delete()
        except discord.errors.NotFound:
            pass  # oh well.
        if penalty != 1:
            try:
                offensive_word = result[1]
                do_warn = result[2]
                if penalty == 2:  # ban
                    await message.author.ban(reason=f'Banned for saying word {offensive_word}\n'
                                                    f'Full message: {message.content}')
                if penalty == 3:  # kick
                    await message.author.kick(reason=f'Kicked for saying word {offensive_word}\n'
                                                     f'Full message: {message.content}')
                if penalty == 4:  # mute
                    role = message.guild.get_role(get_server_config(message.guild.id, 'mute_role', int))
                    await message.author.add_roles(role)
                    mute.add_mutes(message.guild.id, role.id, message.author.id, bot.user.id, "1 hour")
                if do_warn:  # warn
                    moderation.warn(message.guild.id, message.author.id,
                                    bot.user.id, bot.user.name, message.channel.id,
                                    f'Warned for saying word {offensive_word}\n'
                                    f'Full message: {message.content}')
            except discord.errors.Forbidden:
                await message.channel.send(get_language_str(message.guild.id, 5))
                # People expect the bot to work without even giving them the perms.


@bot.event
async def on_ready():
    logging.info('drop-discord is ready: everything should have loaded successfully.')
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
    DiscordComponents(bot)
    await get_github_config()
    print(f'I am {bot.user} (user ID {bot.user.id}), in {len(bot.guilds)} guilds.')

    try:
        if ownerId:
            owner_refresh.start()
        activity_changer.start()
        inactivity_func.start()
        unban_task.start()
    except RuntimeError:
        # whoops, already started.
        pass

    if get_config_parameter('geniusApi', str):
        init_genius(get_config_parameter('geniusApi', str))

    global bot_mention
    global bot_mention_mobile
    bot_mention = f'<@!{bot.user.id}>'
    bot_mention_mobile = f'<@{bot.user.id}>'
    return


logging.info('on_ready has been configured')

message_count = {}

excluded_users = get_config_parameter('excluded_users', list)


@bot.check
async def command_check(ctx):
    if ctx.author.id in excluded_users:
        return False
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
        await check_message(message)
    if message.author.id == bot.user.id:
        return  # To prevent the bot itself from triggering things.
    if message.author.id in excluded_users:
        return
    global message_count
    if message.guild and get_server_config(message.guild.id, 'inactivity_func', bool) and \
            message.channel.id in get_server_config(message.guild.id, 'inactivity_channels', list):
        if message.channel.id in message_count:
            count = message_count[message.channel.id]
        else:
            count = 0
        message_count[message.channel.id] = count + 1
    if (message.content == bot_mention) or (message.content == bot_mention_mobile):
        if message.author.id not in get_server_config(message.guild.id, 'asked_prefix', list):
            # remind user about the prefix
            asked = get_server_config(message.guild.id, 'asked_prefix', list)
            asked.append(message.author.id)
            write_server_config(message.guild.id, 'asked_prefix', asked)
            await message.channel.send(get_language_str(message.guild.id, 4).format(
                get_server_config(message.guild.id, 'prefix', str)))
        else:
            # taunt the user
            to_send = get_language_str(get_server_config(message.guild.id, 'language', str), 0)
            await message.channel.send(random.choice(to_send).format(message))
            return

    if '(╯°□°）╯︵ ┻━┻' in message.content and message.guild:
        if get_server_config(message.guild.id, 'tableflip', bool):
            async with message.channel.typing():
                lang = get_server_config(message.guild.id, 'language', str)
                to_send = get_language_str(lang, 2)
                to_send = random.choice(to_send)
                await asyncio.sleep(0.75)
                await message.channel.send(to_send.format(message))


@bot.command(
    name='activity',
    description='This command will change the bot\'s current activity '
                'as well as reset the timer for activity_changer (the task loop).',
    usage='[SteamVR | playing something | listening Red Vox | watching """anime""" | 17]',
    brief='Changes the bot\'s activity'
)
@commands.is_owner()
async def activity_changer_command(ctx, *, activity=None):
    if activity:
        activity_list = activity.split(' ')
        if activity_list[0] in [x.name for x in discord.ActivityType]:
            activity_type = activity_list[0]
            activity_name = " ".join(activity_list[1:])
        else:
            activity_type = 'playing'
            activity_name = activity
    else:
        activity = await get_new_activity(ctx.author, listening_activities=bot.listening_activities)
        activity_type = activity[0]
        activity_name = activity[1]
    await ctx.reply(content=f'{activity_type.title()} {activity_name}')
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType[activity_type], name=activity_name))


@bot.listen()
async def on_message_edit(_before, after):
    if after.guild:
        await check_message(after)


logging.info('on_message has been configured')


@tasks.loop(minutes=2, count=None, reconnect=True)
async def owner_refresh():
    logging.info("Refreshing owner member and user objects")
    global ownerUser
    ownerUser = bot.get_user(ownerId)
    for member in bot.get_all_members():
        if member.id == ownerId:
            global ownerMember
            ownerMember = member


@tasks.loop(minutes=5, count=None, reconnect=True)
async def activity_changer():
    if ownerMember:
        activity = await get_new_activity(ownerMember, listening_activities=bot.listening_activities)
    else:
        activity = await get_new_activity(listening_activities=bot.listening_activities)
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


@tasks.loop(minutes=1)
async def unban_task():
    unbans = check_bans()
    if unbans:
        for toUnban in unbans:
            guild_id = toUnban.guild_id
            guild = bot.get_guild(guild_id)
            user_id = toUnban.user_id
            ban_list = await guild.bans()
            for entry in ban_list:
                if entry.user.id == int(user_id):
                    # We have found the correct user
                    await guild.unban(entry.user, reason="Their temp-ban period is over.")


logging.info('Task loops has been configured')


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
            await ctx.send(content=get_language_str(get_server_config(ctx.guild.id, 'language', str), 7),
                           file=discord.File(error_file, 'error.txt'))


@bot.event
async def on_guild_join(guild):
    if guild.owner.id in excluded_users:
        await guild.leave()
        return
    with open("data/data_clear.json", "r", encoding="utf-8", newline="\n") as f:
        data_clear = json.load(f)
        if str(guild.id) in data_clear:
            # Data deletion has been queued, but will need to be cancelled.
            system_channel = guild.system_channel
            if system_channel:
                try:
                    await system_channel.send("Woah there. It seems like this server had their data deletion queued. "
                                              "Since someone invited me back, this data deletion queue will be "
                                              "cancelled. If you'd like to queue it back, please run the `cleardata` "
                                              "command again (and don't invite me back in this server).")
                except discord.errors.Forbidden:
                    pass  # it's not like it's *super* important anyways...
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


@bot.event
async def on_member_update(_before, after):
    if not (after.id == bot.owner_id):
        return
    listening_activity = get_listening_to(after.activities, guess_listening=False)
    if listening_activity:
        artist = listening_activity[1]
        if artist not in bot.listening_activities:
            bot.listening_activities.append(listening_activity[1])


if get_config_parameter('dev_token', bool):
    logging.info("Developer mode activated, passing through developer token.")
    token_path = "data/devtoken.txt"
else:
    logging.info('dev_token not enabled; using regular token')
    token_path = "data/token.txt"

if get_config_parameter('jishaku', bool) or get_config_parameter('dev_token', bool):
    try:
        bot.load_extension('jishaku')
    except discord.ext.commands.errors.ExtensionNotFound:
        logging.warning("Could not load Jishaku. You can install it using \"pip install jishaku\". "
                        "Jishaku may be helpful for debugging.")
    else:
        logging.info("Jishaku loaded: continuing...")

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

logging.info('Connecting to Discord...')
bot.run(specified_token, bot=True, reconnect=True)
