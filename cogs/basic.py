import json
import os
import random
import sys
from datetime import datetime as d

import discord
from discord.ext import commands
from data.extdata import get_config_parameter, get_steam_played_game, SteamModes, get_discpy_version


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
        name="hostinfo",
        description="Retrieves info from current bot host.",
        aliases=["host_info"],
        brief='Gets info from the host'
    )
    async def hostinfo_command(self, ctx):
        if os.name == 'nt':
            desc = f"Running on Windows ({os.name})"
        elif os.name == "darwin":
            desc = f"Running on macOS ({os.name})"
        elif os.name == 'posix':
            desc = f"Running on Posix/Linux ({os.name})"
        else:
            desc = f"Running on *something* ({os.name})"
        desc = desc + f"\nPython {sys.version}"
        desc = desc + f"\nDiscord.py {get_discpy_version()}"
        embed = discord.Embed(
            title="Host info",
            description=desc,
            color=random.choice(color_list)
        )
        if get_config_parameter('useSteamRecentlyPlayed', int) != 0:
            mode = get_config_parameter('useSteamRecentlyPlayed', int)
            embed.add_field(
                name='Steam integration',
                value=f"Mode: {mode} ({SteamModes.get(mode)})\n"
                      f"Random played game: {get_steam_played_game()}"
            )
        await ctx.send(embed=embed)

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


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
