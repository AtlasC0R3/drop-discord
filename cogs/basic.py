import json
import random
from datetime import datetime as d

import discord
from discord.ext import commands
from data.extdata import get_artist, get_lyrics
from tswift import TswiftError


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
        start = d.timestamp(d.now())
        msg = await ctx.reply(content="Huh?")

        await msg.edit(content=f'Pong!\nIt took me {(d.timestamp(d.now()) - start) * 1000}ms'
                               f'.')
        return

    @commands.command(
        name='8ball',
        description='The 8ball command',
        aliases=['eightball'],
        brief='It\'s an 8ball, what more do you want?'
    )
    async def _8ball_command(self, ctx):
        responses = [
            'It is certain.',
            'It is decidedly so.',
            'Without a doubt',
            'Yes - definitely.',
            'You may rely on it.',
            'As I see it, yes.',
            'Most likely.',
            'Outlook good.',
            'Yes.',
            'Signs point to yes.',
            'Reply hazy, try again.',
            'Ask again later.',
            'Better not tell you now.',
            'Cannot predict now.',
            'Concentrate and ask again.',
            "Don't count on it.",
            'My reply is no.',
            'My sources say no.',
            'Outlook not so good.',
            'Very doubtful.'
        ]
        await ctx.reply(content=f"{random.choice(responses)}")

    @commands.command(
        name='say',
        description='Repeats what the user says as arguments.',
        aliases=['repeat', 'parrot', 'echo'],
        usage='<text>',
        brief='Repeats what the user said'
    )
    async def say_command(self, ctx):
        msg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        text = msg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if text == '':
            await ctx.reply(content='hey, I can\'t send literally nothing.')
            return
        else:
            await ctx.send(text)

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
            await ctx.send('What text would you like to owofy?')
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
            await ctx.send(f"Uh oh, the text is over 2000 characters long, which is the maximum number of characters "
                           f"allowed in a message. *(Current length is {len(text)}, action cancelled)*")
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
        await ctx.send(content='What would you like the title to be?')

        # Wait for a response and get the title
        msg = await self.bot.wait_for('message', check=check)
        if len(msg.content) < 257:  # Checks if title's length is bigger than 256.
            title = msg.content
        else:
            await ctx.send(f"Uh oh, the title's length is higher than 256! Maximum length allowed is 256. "
                           f"*(Requested title's length is {len(msg.content)}, action cancelled.)*")
            return

        # Next, ask for the content
        await ctx.send(content='What would you like the Description to be?')
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
        description='Uses MetroLyrics (or the Python library "tswift") to get lyrics.\n'
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
            try:
                if len(lyrics.lyrics) >= 2048:
                    lyricstr = ''.join(list(lyrics.lyrics)[:2045]) + '...'
                else:
                    lyricstr = lyrics.lyrics
            except TswiftError:
                lyricstr = 'No lyrics available'
            embed = discord.Embed(
                title=f'*{lyrics.title}* by *{lyrics.artist}*',
                description=lyricstr,
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.set_footer(
                text='obtained using MetroLyrics'
            )
            await ctx.reply(embed=embed)
            await msg.delete()
        elif type(args) is str:
            # get artist
            msg = await ctx.send(f'Searching for songs by {args}')
            artist = get_artist(args)
            if not artist:
                await ctx.reply('Could not find that artist. Sorry.')
                return
            embed = discord.Embed(
                title=f'Random songs by *{artist[0]}*',
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            embed.set_footer(
                text='obtained using MetroLyrics'
            )
            for song in artist[1]:
                songname = song[0]
                lyrics = '\n'.join(song[1]).removesuffix('\n')
                if not lyrics:
                    lyrics = 'No lyrics available. *Sorry, I guess...*'
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
            await ctx.reply("Insert either an artist's name or a song, otherwise I can't work with literally nothing!")

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
                  "(https://github.com/psf/requests/blob/master/LICENSE)"
        )  # And of course, you should probably list any other open-source dependencies you used.
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
