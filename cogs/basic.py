import json
from datetime import datetime as d

import discord
from discord.ext import commands
from data.extdata import get_language_str
from tswift import TswiftError

import drop
from drop.basic import *


with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


# New - The Cog class must extend the commands.Cog class
class Basic(commands.Cog):
    """
    Just a regular set of basic commands every Discord bot should have.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='ping',
        description='The ping command',
        aliases=['p'],
        brief='Check the bot\'s latency'
    )
    async def ping_command(self, ctx):
        huh = get_language_str(ctx.guild.id, 8)
        pong = get_language_str(ctx.guild.id, 9)
        start = d.timestamp(d.now())
        msg = await ctx.reply(content=huh)
        await msg.edit(content=pong.format((d.timestamp(d.now()) - start) * 1000))
        # Do not move into rewrite

    @commands.command(
        name='8ball',
        description='The 8ball command',
        aliases=['eightball'],
        brief='It\'s an 8ball, what more do you want?'
    )
    async def _8ball_command(self, ctx):
        responses = get_language_str(ctx.guild.id, 10)
        await ctx.reply(random.choice(responses))

    @commands.command(
        name='say',
        description='Repeats what the user says as arguments.',
        aliases=['repeat', 'parrot', 'echo'],
        usage='<text>',
        brief='Repeats what the user said'
    )
    async def say_command(self, ctx, *, repeat=None):

        # Next, we check if the user actually passed some text
        if not repeat:
            await ctx.reply(get_language_str(ctx.guild.id, 11))
            return
        else:
            await ctx.send(repeat)

    @commands.command(
        name='owofy',
        description='I hate myself, and I\'m not sorry for creating this.\n'  # Well what, I'm saying the truth here!
                    'Do I really have to explain what this does?.. yeah?.. ah dammit.\n'
                    'It converts the text to owospeak. There. I said it.',
        aliases=['owoify', 'owospeak'],
        usage='<text (can also be sent as a separate message)>',
        brief='Why...'
    )
    async def owofy_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author
        msg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        text = msg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if text == '':
            # User didn't specify the text, which means we'll have to ask for it.
            await ctx.send(get_language_str(ctx.guild.id, 12))
            msg = await self.bot.wait_for('message', check=check)
            text = msg.content
            pass

        # now the pain and suffering shall happen
        no_please_stop = {'r': 'w',
                          'l': 'w',
                          'R': 'W',
                          'L': 'W',
                          'na': 'nya',  # please stop.
                          'ne': 'nye',
                          'ni': 'nyi',
                          'no': 'nyo',
                          'nu': 'nyu',
                          'Na': 'Nya',  # oh no the capitalization
                          'Ne': 'Nye',
                          'Ni': 'Nyi',
                          'No': 'Nyo',
                          'Nu': 'Nyu',
                          'nA': 'nyA',  # aaaaaaaaaaaaaaaaaaaaaaaaaa
                          'nE': 'nyE',
                          'nI': 'nyI',
                          'nO': 'nyO',
                          'nU': 'nyU',
                          'NA': 'NYA',  # this is mental torture.
                          'NE': 'NYE',
                          'NI': 'NYI',
                          'NO': 'NYO',
                          'NU': 'NYU'}  # I f***ing hate myself.
        for key, value in no_please_stop.items():
            text = text.replace(key, value)

        why_do_you_do_this = [' OwO', ' @w@', ' #w#', ' UwU', ' ewe', ' -w-', ' \'w\'', ' ^w^', ' >w<', ' ~w~', ' ¬w¬',
                              ' o((>ω< ))o', ' (p≧w≦q)', ' ( •̀ ω •́ )y', ' ✪ ω ✪', ' (。・ω・。)', ' (^・ω・^ )']
        # why did i put so many in here

        while '!' in text:
            text = text.replace('!', random.choice(why_do_you_do_this), 1)

        if not len(text) < 2000:
            await ctx.send(get_language_str(ctx.guild.id, 13).format(len(text)))
            return
        await ctx.reply(text)  # the pain has been done.

    @commands.command(
        name='embed',
        description='Kinda the same as the "repeat" command, however now with embed!',
        aliases=['sayembed', 'echoembed', 'repeatembed'],
        brief='Sends an embed'
    )
    async def embed_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author
        await ctx.send(get_language_str(ctx.guild.id, 14))

        # Wait for a response and get the title
        msg = await self.bot.wait_for('message', check=check)
        if len(msg.content) < 257:  # Checks if title's length is bigger than 256.
            title = msg.content
        else:
            await ctx.send(get_language_str(ctx.guild.id, 15).format(len(msg.content)))
            return

        # Next, ask for the content
        await ctx.send(get_language_str(ctx.guild.id, 16))
        msg = await self.bot.wait_for('message', check=check)
        desc = msg.content
        # For some reason bot embed descriptions have no limits.
        # https://cdn.discordapp.com/attachments/661616167378485249/780232830180655155/unknown.png

        # Finally make the embed and send it
        msg = await ctx.reply(content='Now generating the embed...')
        embed = discord.Embed(
            title=title,
            description=desc,
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=self.bot.user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await msg.edit(
            embed=embed,
            content=None
        )

    @commands.command(
        name='lyrics',
        description='Uses either MetroLyrics (or the Python library "tswift") or Genius to get lyrics.\n'
                    'Can be used in a multitude of ways: to find random songs by an artist, to find lyrics for a song '
                    'by an artist or to find lyrics using what the user is currently playing on Spotify.\n',
        aliases=['lyric', 'getsong', 'getartist'],
        brief='Gets lyrics',
        usage='[In The End - Linkin Park|Already Over / Red|Imagine Dragons]'
    )
    async def lyrics_command(self, ctx, *, args=None):
        separator = [' / ', ' - ', ' \\ ']
        if args:
            for item in separator:
                if item in args:
                    args = args.split(item)
                    break
        else:
            # check if user playing something on spotefiye
            # discord when will you add support for tidal /s
            activities = ctx.author.activities
            for activity in activities:
                if isinstance(activity, discord.activity.Spotify):
                    args = [activity.title, activity.artist.split(';')[0]]
                    break
                elif isinstance(activity, discord.activity.Activity):
                    # Maybe the user is using PreMiD, or rich presence on some app?
                    if activity.application_id == 463151177836658699:  # YouTube Music
                        args = [activity.details, activity.state.split(' - ')[0]]
                        # curse how yt music is so inconsistent
                        break
                    elif activity.application_id == 589905203533185064:  # Rhythmbox (not in PreMiD, I just use it):
                        args = [activity.details.split(' - ')[0], activity.details.split(' - ')[-1]]
                        break

        if type(args) is list:
            song = args[0]
            artist = args[-1]
            msg = await ctx.send(f'Searching for "{song}" by {artist}')
            lyrics = get_lyrics(artist=artist, title=song)
            if type(lyrics) is lyricsgenius.genius.Song:
                # that is Genius.
                obtained_from = 'Genius'
                thumbnail = lyrics.song_art_image_url
                url = lyrics.url
            else:
                obtained_from = 'MetroLyrics'
                thumbnail = None
                url = None
            try:
                if len(lyrics.lyrics) >= 2048:
                    lyric_str = ''.join(list(lyrics.lyrics)[:2045]) + '...'
                else:
                    lyric_str = lyrics.lyrics
            except TswiftError:
                lyric_str = get_language_str(ctx.guild.id, 17)
                obtained_from = 'common sense'
            embed = discord.Embed(
                title=get_language_str(ctx.guild.id, 20).format(lyrics.title, lyrics.artist),
                description=lyric_str,
                color=random.choice(color_list),
                url=url
            )
            if thumbnail:
                embed.set_thumbnail(url=thumbnail)
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.set_footer(
                text=f'obtained using {obtained_from}'
            )
            await ctx.reply(embed=embed)
            await msg.delete()
        elif type(args) is str:
            # get artist
            msg = await ctx.send(f'Searching for songs by {args}')
            obtained = get_artist(args)
            artist = obtained[1]
            service = obtained[0]
            if not artist:
                await ctx.reply(get_language_str(ctx.guild.id, 18))
                return
            if service == 'Genius':
                artist_name = artist[0]
                title = f'Popular songs by *{artist_name}*'
            elif service == 'MetroLyrics':
                title = f'Random songs by *{artist[0]}*'
                artist = obtained[1]
            else:
                title = 'Some songs.'
            embed = discord.Embed(
                title=title,
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.set_footer(
                text=f'obtained using {service}'
            )
            for song in artist[1]:
                song_name = song[0]
                lyrics = '\n'.join(song[1])
                url = song[2]
                if not lyrics:
                    lyrics = get_language_str(ctx.guild.id, 17)
                else:
                    if url:
                        lyrics = lyrics + f'\n<{url}>'
                    else:
                        lyrics = lyrics + '\n...'
                embed.add_field(
                    name=f'*{song_name}*',
                    value=lyrics,
                    inline=False
                )
            await ctx.reply(embed=embed)
            await msg.delete()
        else:
            await ctx.reply(get_language_str(ctx.guild.id, 19))

    @commands.command(
        name='license',
        description="This is a command that will return this bot's license, along with other dependencies' open-source "
                    "licenses.",
        brief='Returns open-source licenses'
    )
    async def license_command(self, ctx):
        embed = discord.Embed(
            title='Drop',
            description="This software is licensed using the Apache 2.0 license "
                        "(https://github.com/AtlasC0R3/drop-bot/blob/main/LICENSE) "
                        "as free and open-source software.",
            color=0x29b6f6
        )
        # embed.add_field(
        #     name='Changes made to this software',
        #     value='i uhhhhh i changed the way mutes were done',
        #     inline=False
        # )
        # You could uncomment this to list the changes made to this software, if you have made any.
        # And of course, if you want to use this method of doing so.
        embed.add_field(
            name='Open-source dependencies used',
            value="Discord.py, licensed under MIT License (https://github.com/Rapptz/discord.py/blob/master/LICENSE)\n"
                  "discord-pretty-help, licensed under MIT License "
                  "(https://github.com/stroupbslayen/discord-pretty-help/blob/master/LICENSE)\n"
                  "parsedatetime, licensed under Apache 2.0 license, no changes made "  # hopefully no changes made >:(
                  "(https://github.com/bear/parsedatetime/blob/master/LICENSE.txt)\n"
                  "tswift, licensed under BSD 3-Clause license "
                  "(https://github.com/brenns10/tswift/blob/master/LICENSE.md)\n"
                  "requests, licensed under Apache 2.0 license, no changes made "
                  "(https://github.com/psf/requests/blob/master/LICENSE)\n"
                  "LyricsGenius, licensed under MIT License "
                  "(https://github.com/johnwmillr/LyricsGenius/blob/master/LICENSE.txt)\n"
                  "DuckDuckPy, licensed under MIT License "
                  "(https://github.com/ivankliuk/duckduckpy/blob/master/LICENSE)",
            inline=False
        )  # And of course, you should probably list any other open-source dependencies you used.
        embed.add_field(
            name='Drop licenses *(licenses related to the core software and not the actual Discord bot)*',
            value=drop.licenses(),
            inline=False
        )
        await ctx.send(embed=embed)
        # I'd rather not translate this command.

    @commands.command(
        name='search',
        description="This uses DuckDuckGo (or duckduckpy) to search whatever on the Internet. "
                    "It will return whatever it finds.",
        brief='Does a DuckDuckGo search'
    )
    async def search_command(self, ctx, *, to_search):
        response = search(to_search)
        if response is not None:
            embed = discord.Embed(
                title=response['title'],
                description=response['description'],
                url=response['url']
            )
            embed.set_footer(
                text=response['source']
            )
            if response['image']:
                embed.set_thumbnail(
                    url=response['image']
                )
            if True:
                for field in response['fields']:
                    embed.add_field(
                        name=field['name'],
                        value=field['value'],
                        inline=False
                    )
            await ctx.send(embed=embed)
        else:
            await ctx.reply(get_language_str(ctx.guild.id, 122))


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
