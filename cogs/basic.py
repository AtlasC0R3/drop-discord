import json
import random
from datetime import datetime as d

import discord
from discord.ext import commands
from data.extdata import get_artist, get_lyrics, get_language_str
from tswift import TswiftError
import lyricsgenius
import duckduckpy


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
                    # Maybe the user is using PreMiD?
                    if activity.application_id == 463151177836658699:  # YouTube Music
                        args = [activity.details, activity.state.split(' - ')[0]]
                        # curse how yt music is so inconsistent
                        break

        if type(args) is list:
            song = args[0]
            artist = args[-1]
            msg = await ctx.send(f'Searching for "{song}" by {artist}')
            lyrics = get_lyrics(artist, song)
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
                    lyricstr = ''.join(list(lyrics.lyrics)[:2045]) + '...'
                else:
                    lyricstr = lyrics.lyrics
            except TswiftError:
                lyricstr = get_language_str(ctx.guild.id, 17)
                obtained_from = 'common sense'
            embed = discord.Embed(
                title=get_language_str(ctx.guild.id, 20).format(lyrics.title, lyrics.artist),
                description=lyricstr,
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
                artistname = artist[0]
                title = f'Popular songs by *{artistname}*'
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
                songname = song[0]
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
                    name=f'*{songname}*',
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
                  "(https://github.com/ivankliuk/duckduckpy/blob/master/LICENSE)"
        )  # And of course, you should probably list any other open-source dependencies you used.
        await ctx.send(embed=embed)
        # I'd rather not translate this command.

    @commands.command(
        name='search',
        description="This uses DuckDuckGo (or duckduckpy) to search whatever on the Internet. "
                    "It will return whatever it finds.",
        brief='Does a DuckDuckGo search'
    )
    async def search_command(self, ctx, *, to_search):
        response = duckduckpy.query(to_search, user_agent=u'duckduckpy 0.2', no_redirect=False, no_html=True,
                                    skip_disambig=True, container='dict')
        if response['infobox']:
            infobox = response['infobox']['content']
            image = None
            if response['image']:
                if response['image'].startswith('/'):
                    image = 'https://duckduckgo.com' + response['image']
                else:
                    image = response['image']
            embed = discord.Embed(
                title=response['heading'],
                description=response.get('abstract_text'),
                url=response['abstract_url'],
                color=random.choice(color_list)
            )
            if image:
                embed.set_thumbnail(
                    url=image
                )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.set_footer(
                text=response['abstract_source']
            )
            for info in infobox:
                if info['data_type'] == 'string':
                    if len(info['value']) >= 256:
                        value = ''.join(list(info['value'])[:253]) + '...'
                    else:
                        value = info['value']
                    embed.add_field(
                        name=info['label'],
                        value=value,
                        inline=False
                    )
            await ctx.reply(embed=embed)
        elif response['related_topics']:
            description = response.get('abstract_text')
            if description:
                description = description + f"*({response['abstract_source']})*"
            embed = discord.Embed(
                title=response['heading'],
                description=description,
                url=response.get('abstract_url'),
                color=random.choice(color_list)
            )
            for topic in response['related_topics']:
                if topic.get('topics'):
                    pass  # not really what we're looking for
                else:
                    name = topic.get('text')
                    if len(name) >= 256:
                        name = ''.join(list(name)[:253]) + '...'
                    if ' - ' in name:
                        things = name.split(' - ')
                        name = things[0]
                        description = ' - '.join(things[1:]) + '\n' + f"({topic.get('first_url')})"
                    else:
                        description = topic.get('first_url')
                    embed.add_field(
                        name=name,
                        value=description,
                        inline=False
                    )
            await ctx.reply(embed=embed)
        else:
            await ctx.reply(get_language_str(ctx.guild.id, 122))


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
