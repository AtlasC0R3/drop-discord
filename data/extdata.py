import json
import os
import aiohttp
import random
import discord
import drop.types
import re
import logging
from drop import config, errors
from discord.ext.commands.bot import Bot

from discord_components import Button, ButtonStyle

exampleServerConfig = {
    "prefix": "!",
    "share_error_logs": False,
    "asked_prefix": [],
    "inactivity_func": False,
    "inactivity_channels": [],
    "mute_role": 0,
    "disabled_commands": [],
    "disabled_cogs": [],
    "no_no_words": {},
    "tableflip": True,
    "language": "default",
    "antiraid": {}
}

exampleConfig = {}

langs = {}
for lang in os.listdir('lang/'):
    if lang.endswith('.json'):
        langname = lang.split('.')[0].lower()  # i need to stop doing these ass long code lines
        langs[langname] = json.load(open('lang/' + lang))


async def get_github_config():
    global exampleConfig
    async with aiohttp.ClientSession() as session:
        async with session.get('https://raw.githubusercontent.com/AtlasC0R3/drop-discord/main/data/config.json') as r:
            if r.status == 200:
                exampleConfig = json.loads(await r.text())


def get_default_language(idx: int):
    return langs['default'][idx]


def get_all_languages():
    return langs.keys()


def get_language_str(language: str or int, idx: int):
    if type(language) is int:
        language = get_server_config(language, 'language', str)
    try:
        to_return = langs[language][idx]
        if not to_return:
            to_return = get_default_language(idx)
            # Sometimes people are lazy and might not want to translate a string.
            # or that i updated the bot and that the string couldn't be obtained
            # wait in that case it'd return indexerror, i'm dumb. like really dumb. like supremely dumb, holy wow.
    except (IndexError, KeyError):
        return get_default_language(idx)
    return to_return


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
    try:
        config_param = config.get_config_parameter(param, paramtype)
    except errors.ConfigParameterNotFound:
        config_param = exampleConfig.get(param)
        config.write_config_parameter(param, config_param)
    return paramtype(config_param)


def get_server_config(serverid, param, paramtype):
    try:
        return config.get_server_config(serverid, param, paramtype)
    except errors.ConfigParameterNotFound:
        config_param = exampleServerConfig.get(param)
        config.write_server_config(serverid, param, config_param)
        return config_param
    except errors.ConfigNotFound:
        config.write_entire_server_config(serverid, exampleServerConfig)
        return paramtype(exampleServerConfig.get(param))


def get_entire_server_config(serverid):
    return config.get_entire_server_config(serverid)


def write_server_config(serverid, param, value):
    config.write_server_config(serverid, param, value)


async def get_steam_user_recently_played():
    steamapiconfig = get_config_parameter('steamApi', dict)
    for dictkey, value in steamapiconfig.items():
        if not value:
            if not dictkey == "excludedGames":
                logging.warning(f'Value {dictkey} undefined, playing Steam instead.\n'
                                f'Please disable "useSteamRecentlyPlayed" in config.json, '
                                f'or fill in the correct values in steamApi.\n'
                                f'If you need help, you can check out '
                                f'https://github.com/AtlasC0R3/drop-discord/wiki/Configuring-the-Steam-integration')
                return 'Steam'
    userid = steamapiconfig.get('userId')
    key = steamapiconfig.get('key')
    steamurl = \
        f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v1' \
        f'?key={key}' \
        f'&steamid={userid}' \
        f'&count=0'
    async with aiohttp.ClientSession() as session:
        async with session.get(steamurl) as r:
            if r.status == 200:
                userdata = await r.json()
            else:
                if r.status == 403:
                    logging.error("Invalid API key passed, falling back to playing Steam.\n"
                                  "Please disable \"useSteamRecentlyPlayed\" in config.json, "
                                  "or fill in the correct values in steamApi.\n"
                                  "If you need help, you can check out "
                                  "https://github.com/AtlasC0R3/drop-discord/wiki/Configuring-the-Steam-integration")
                    return 'Steam'
                elif r.status == 500:
                    logging.error("Invalid user ID passed, falling back to playing Steam.\n"
                                  "Please disable \"useSteamRecentlyPlayed\" in config.json, "
                                  "or fill in the correct values in steamApi.\n"
                                  "If you need help, you can check out "
                                  "https://github.com/AtlasC0R3/drop-discord/wiki/Configuring-the-Steam-integration")
                    return 'Steam'
                elif r.status != 200:
                    logging.error(f"Something went wrong with the Steam API callout, falling back to playing Steam.\n"
                                  f"Error code {r.status}, in case you may need it.")
                    return 'Steam'
    return userdata


async def get_steam_played_game():
    games = await get_steam_recently_played()
    game = random.choice(games)
    if game:
        return game
    else:
        return await get_steam_played_game()


async def get_steam_recently_played():
    steamapiconfig = get_config_parameter('steamApi', dict)
    userdata = await get_steam_user_recently_played()
    played_games = []
    userdata = userdata.get('response').get('games')
    for game in userdata:
        played_games.append(game.get('name'))
    excluded_games = steamapiconfig.get('excludedGames')
    for no in excluded_games:
        for game in played_games:
            if game:
                if no.lower() in game.lower():
                    played_games = [x for x in played_games if x != game]
            else:
                played_games = [x for x in played_games if x != game]
    return played_games


to_replace = {
    '<b>': '**',
    '</b>': '**',
    '<p>': '\n**',
    '</p>': '**\n',
    '</li>': '\n'
}


def format_html(str_input: str):
    for old, new in to_replace.items():
        str_input = str_input.replace(old, new)
    p = re.compile(r'<.*?>')
    return p.sub('', str_input)


def get_listening_to(activities: discord.Member.activities, guess_listening=True):
    """
    yeah
    :param activities: the member's activities
    :param guess_listening: whether the bot will guess the listening activity if it cant find it
    :return: [title, artist]
    """
    for activity in activities:
        if isinstance(activity, discord.activity.Spotify):
            return [activity.title, activity.artist.split(';')[0]]
        elif isinstance(activity, discord.activity.Activity):
            # Maybe the user is using PreMiD, or rich presence on some app plugin whatever?
            if activity.application_id == 463151177836658699:  # YouTube Music
                return [activity.details, activity.state.split(' - ')[0]]
                # curse how yt music is so inconsistent
            elif activity.application_id == 589905203533185064:  # Rhythmbox (not in PreMiD, I just use it):
                return [activity.details.split(' - ')[0], activity.details.split(' - ')[-1]]
            elif activity.application_id == 404277856525352974:  # SMTCRP, not in PreMiD, by theLMGN
                return [activity.details.split(' - ')[-1], activity.state.replace("👥 ", "")]
            elif activity.application_id == 409394531948298250:  # MusicBee
                return [activity.state, activity.details.split(' - ')[0]]
            elif activity.application_id == 826521040275636325:  # Dopamine
                return [activity.details, activity.state.replace('by ', '', 1)]
            elif activity.application_id == 435587535150907392:  # discordrp-mpris
                things = activity.details.split('\n')
                return [things[0], things[1].replace('by ', '', 1).split(' & ')[0]]
            elif guess_listening:
                # Try guessing.
                title = None
                artist = None
                if activity.state:
                    if activity.state[:3] == 'by ':
                        artist = activity.state.replace('by ', '', 1)
                        title = activity.details
                    elif ' - ' in activity.details:
                        if ('playing' in activity.state.lower()) or ('paused' in activity.state.lower()):
                            title = activity.details.split(' - ')[0]
                            artist = activity.details.split(' - ')[-1]
                        else:
                            title = activity.state
                            artist = activity.details.split(' - ')[0]
                    if title and artist:
                        return [title, artist]


previous_activity = ""


async def get_new_activity(user_member=discord.Member, listening_activities=None):
    if listening_activities is None:
        listening_activities = []
    activity = []

    if user_member:
        if user_member.activity and get_config_parameter('syncActivityWithOwner', bool):
            music_activity = get_listening_to(user_member.activities)
            if music_activity:
                activity_type = 'listening'
                # activity_name = f"{music_activity[0]} by {music_activity[1]}"
                # Uncomment this if you want it to look like "Listening to In The End by Linkin Park"
                activity_name = music_activity[1]
            else:
                activity_type = 'playing'
                activity_name = user_member.activity.name
            activity = [activity_type, activity_name]

    with open("data/activities.json", encoding='utf-8', newline="\n") as file:
        activity_list = json.load(file)

    if get_config_parameter('useSteamRecentlyPlayed', int) == 1:
        activity = ['playing', await get_steam_played_game()]
    elif get_config_parameter('useSteamRecentlyPlayed', int) == 2:
        for game in await get_steam_recently_played():
            activity_list.append(['playing', game])

    for artist in listening_activities:
        activity_list.append(['listening', artist])

    if not activity:
        activity = random.choice(activity_list)
    # I would write something here to check if the activity is the same as the old activity,
    # but I'm too lazy to do that. I have a problem, I know.

    global previous_activity
    if activity[1].lower() == previous_activity.lower():
        return await get_new_activity(user_member=user_member,
                                      listening_activities=listening_activities)
    else:
        previous_activity = activity[1]
        return activity


def check_banword_filter(message: str, guild_id: list):
    result = 0
    offensive_word = ""
    warn = False
    for item in get_server_config(guild_id, 'no_no_words', dict):
        if item in message.lower().replace(" ", ""):
            result = 1
            offensive_word = item
            penalties = get_server_config(guild_id, 'no_no_words', dict)
            if penalties.get(item):
                penalties = penalties.get(item)
                if "ban" in penalties:
                    result = 2
                elif "kick" in penalties:
                    result = 3
                elif "mute" in penalties:
                    result = 4
                if "warn" in penalties:
                    warn = True
    return_list = [result, offensive_word, warn]
    return return_list


async def wait_for_user(ctx, bot, msg: discord.Message, say_action_cancelled=True):
    def check(ms):
        return ms.channel == ctx.message.channel and ms.author == ctx.message.author

    yes = "Yes"
    no = "No"
    what_the_fuck = ""

    await msg.edit(components=[[
        Button(label=yes, style=ButtonStyle.green, emoji='✔️'),
        Button(label=no, style=ButtonStyle.red, emoji='✖️'),
        Button(label=what_the_fuck, style=ButtonStyle.gray, emoji='🗑️')
    ]])

    interaction = await bot.wait_for("button_click", check=check)
    await msg.edit(components=[])
    reply = interaction.component.label
    if reply == yes:
        return True
    elif reply == no:
        if say_action_cancelled:
            await ctx.send(get_language_str(ctx.guild.id, 26))
        return False
    else:
        return False

image_types = (
    '.jpg',
    '.jpeg',
    '.png',
    '.gif',
    '.gifv'
)
video_types = (
    '.mp4',
    '.mov'
)
audio_types = (
    '.wav',
    '.mp3',
    '.ogg',
    '.flac',
    '.m4a'
)
# https://www.reddit.com/r/discordapp/comments/f2kt5r/guide_file_formats_discord_can_embed/

attachment_types = {
    0: "file",
    1: "image",
    2: "video",
    3: "audio"
}


def get_file_type(attachment: discord.Attachment):
    """
     0: nothing, cannot really embed
     1: image
     2: video
     3: audio
    """
    if attachment.content_type.startswith('image/'):
        return 1
    if attachment.content_type.startswith('video/'):
        return 2
    if attachment.content_type.startswith('audio/'):
        return 3
    return 0


def format_warn(warn: drop.types.Warn, bot: Bot):
    warner_id = warn.warner.id
    warner_user = bot.get_user(id=warner_id)
    if not warner_user:
        warner_display = f"{warn.warner.name} (<@{warner_id}>)"
    else:
        warner_display = f"<@{warner_id}>"
    return f"""
            *by {warner_display}, in <#{warn.channel}>*\n*{warn.datetime}*```{warn.reason}```
            """
