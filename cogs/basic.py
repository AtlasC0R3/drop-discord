import json
from datetime import datetime as d
import re

import discord
from discord.ext import commands
from data.extdata import get_language_str, get_listening_to, get_config_parameter

import drop
from drop.basic import *
from drop.steam import search_game, get_protondb_summary, get_steam_app_info
from drop.errors import GameNotFound
from drop.ext import format_html, format_names, random_tumblr_image
from drop.types import Lyrics

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]

steam_key = get_config_parameter("steamApi", dict).get("key")
protondb_colors = {"Platinum": 0xB7C9DE, "Gold": 0xCFB526, "Silver": 0xC1C1C1, "Bronze": 0xCB7F22, "Borked": 0xF90000}


def check_if_steam_nsfw(ctx, game_data: dict):
    if ctx.channel is discord.TextChannel:
        is_channel_nsfw = ctx.channel.is_nsfw()
    else:
        is_channel_nsfw = True
    return (1 in game_data['content_descriptors']['ids']) and (not is_channel_nsfw)


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
        message_latency = (d.timestamp(d.now()) - start) * 1000
        await msg.edit(content=pong.format(message_latency), embed=discord.Embed(
            title="extra details for nerds",
            description=f"message latency: {message_latency}ms\n"
                        f"discord.py latency: {round(self.bot.latency * 1000)}ms"
        ))
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
        elif repeat == "** **":
            await ctx.reply(f"** **... ***{get_language_str(ctx.guild.id, 11)}***")
        elif "@everyone" in repeat or "@here" in repeat:
            await ctx.reply("**No.**")
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

        text = owofy(text)

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
        description='Searches online using the specified query to get lyrics.\n'
                    'You won\'t have to specify the artist either, just a search.\n'
                    'If you\'re listening to something on Spotify and did not pass a query, the bot will '
                    'use the data of the currently playing song. If you are listening to something using '
                    'rich presence, the bot will attempt to use that data to search for lyrics.',
        aliases=['lyric', 'getsong', 'getartist'],
        brief='Gets lyrics',
        usage='[(song title) | (song title) - (artist name)]'
    )
    async def lyrics_command(self, ctx, *, query=None):
        if not query:
            # check if user playing something on spotefiye
            # discord when will you add support for tidal /s
            if not ctx.guild:
                await ctx.send("I can't retrieve your user activity inside private messages, "
                               "so you'll have to manually insert them.")
                return
            user_listening = get_listening_to(ctx.author.activities)
            if user_listening:
                parenthesis_regex = re.compile(r' \(.*?\)')
                query = f"{parenthesis_regex.sub('', user_listening[0]).split(' - ')[0]} - {user_listening[-1]}"
                # string spaghetti
            else:
                await ctx.reply(get_language_str(ctx.guild.id, 19))
                return

        msg = await ctx.send(f'Searching for "{query}"')
        song = await lyrics(query)
        if not song:
            song = Lyrics()
        thumbnail = song.thumbnail
        url = song.url
        title = song.title
        artist = song.artist
        if len(song.lyrics) >= 4096:
            lyric_str = ''.join(list(song.lyrics)[:4093]) + '...'  # Apparently Discord upgraded their character limit.
        else:                                                      # Haven't had much issues yet.
            lyric_str = song.lyrics
        embed = discord.Embed(
            title=get_language_str(ctx.guild.id, 20).format(title, artist),
            description=lyric_str,
            color=random.choice(color_list)
        )
        if url:
            embed.url = url
        if thumbnail:
            embed.set_thumbnail(url=thumbnail)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        embed.set_footer(
            text=song.source,
            icon_url=song.source_icon
        )
        await ctx.reply(embed=embed)
        await msg.delete()

    @commands.command(
        name='license',
        description="This is a command that will return this bot's license, along with other dependencies' open-source "
                    "licenses.",
        brief='Returns open-source licenses'
    )
    async def license_command(self, ctx):
        embed = discord.Embed(
            title='drop-discord',
            description="This software is licensed using the [Apache 2.0 license]"
                        "(https://github.com/AtlasC0R3/drop-discord/blob/main/LICENSE) "
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
            value="Discord.py, licensed under [MIT License](https://github.com/Rapptz/discord.py/blob/master/LICENSE)\n"
                  "discord-pretty-help, licensed under [MIT License]"
                  "(https://github.com/stroupbslayen/discord-pretty-help/blob/master/LICENSE)\n"
                  "discord-py-slash-command, licensed under [MIT License]"
                  "(https://github.com/eunwoo1104/discord-py-slash-command/blob/master/LICENSE)\n"
                  "aiohttp, licensed under [Apache 2.0 license]"
                  "(https://github.com/aio-libs/aiohttp/blob/master/LICENSE.txt), no changes made ",
            inline=False
        )  # And of course, you should probably list any other open-source dependencies you used.
        embed.add_field(
            name='Drop licenses *(licenses related to the core software and not the actual Discord bot)*',
            value=drop.licenses(markdown_links=True),
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
        response = await search(to_search)
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
            if ctx.guild:
                limit = 6
            else:
                limit = None
            for field in response['fields'][:limit]:
                embed.add_field(
                    name=field['name'],
                    value=field['value'] + (('\n' + f"**[Link]({field['url']})**") if field['url'] else ""),
                    # Behold: big fucking nonsense!
                    inline=True
                )
            if response['engine']:
                embed.set_footer(
                    text=response['engine'],
                    icon_url=response['engine_icon']
                )
            await ctx.send(embed=embed)
        else:
            await ctx.reply(get_language_str(ctx.guild.id, 122))

    @commands.command(
        name='protondb',
        description="Fetches results from ProtonDB to know your game's compatibility rating (platinum, gold, silver, "
                    "etc.)\nBecause Linux gaming is awesome.",  # :^)
        brief='Fetches ProtonDB results',
        usage="[220 | Half-Life 2] (note: inputting nothing will default to looking for Half-Life 2)"
    )
    async def protondb_command(self, ctx, *, requested_app="220"):
        if requested_app.isdigit():
            app_id = requested_app
        else:
            try:
                app_id = (await search_game(requested_app))[0]
            except IndexError:
                await ctx.reply(get_language_str(ctx.guild.id, 132))
                return

        try:
            received = await get_protondb_summary(app_id)
        except GameNotFound:
            await ctx.reply(get_language_str(ctx.guild.id, 133))
            return

        tier = received.get("tier").title()
        string_result = received.get("string_result")

        game_data = (await get_steam_app_info(app_id))[str(app_id)]["data"]
        if check_if_steam_nsfw(ctx, game_data):  # fuck my server forcing me to do this to make them shut up
            game_name = "Unnamed NSFW game"
            game_image = \
                "https://upload.wikimedia.org/wikipedia/commons/thumb/9/91/Snake_plant.jpg/1200px-Snake_plant.jpg"
            game_url = ""
        else:
            game_name = game_data["name"]
            game_image = game_data["header_image"]
            game_url = f"https://www.protondb.com/app/{app_id}"
        color = received.get("tier_color")
        if game_data["platforms"]["linux"]:
            string_result = string_result + '\n\n' + get_language_str(ctx.guild.id, 134)

        # await ctx.reply(string_result)
        # await ctx.send(f"Game's {game_name} by the way, here's an image: {game_image}")
        embed = discord.Embed(
            title=game_name,
            description=f"**{tier}**\n{string_result}",
            url=game_url,
            color=color
        )
        embed.set_footer(
            text="ProtonDB",
            icon_url="https://www.protondb.com/sites/protondb/images/favicon.ico"
        )
        embed.set_thumbnail(
            url=game_image
        )
        await ctx.reply(embed=embed)

    @commands.command(
        name='steam',
        description="Fetches results from the Steam store, similar to how you'd post a link to a Steam app.",
        brief='Searches the Steam store',
        usage="[220 | Half-Life 2] (note: inputting nothing will default to looking for Half-Life 2)"
    )
    async def steam_command(self, ctx, *, requested_app="220"):
        if requested_app.isdigit():
            app_id = requested_app
        else:
            try:
                app_id = (await search_game(requested_app))[0]
            except IndexError:
                await ctx.reply(get_language_str(ctx.guild.id, 132))
                return

        game_data = (await get_steam_app_info(app_id))
        if not game_data:
            await ctx.reply(get_language_str(ctx.guild.id, 132))
            return
        game_data = game_data[str(app_id)]["data"]
        if game_data['type'] == 'hardware':
            game_name = game_data["name"]
            game_image = game_data["header_image"]
            description = format_html(game_data["short_description"])
            if game_data.get('website'):
                description += f"\n[Website]({game_data['website']})"
            developers = None
            publishers = None
        else:
            game_name = game_data["name"]
            game_image = game_data["header_image"]
            descriptions = (game_data["about_the_game"],
                            game_data["detailed_description"], game_data["short_description"])
            description = "Descriptions too long in length. Sorry!"
            for desc in descriptions:
                if len(desc) <= 4096:
                    description = format_html(desc)
            developers = format_names(game_data["developers"])
            publishers = format_names(game_data["publishers"])
        if check_if_steam_nsfw(ctx, game_data):
            await ctx.send(f"<@{ctx.author.id}>, what are you doing? :^)")
            return

        embed = discord.Embed(
            title=game_name,
            description=description,
            url=f"http://store.steampowered.com/app/{app_id}"
        )
        if developers:
            if (developers == publishers) or (not publishers):
                embed.set_author(name=developers)
            else:
                embed.set_author(name=f"Developed by {developers}, published by {publishers}")
        embed.set_footer(
            text="Steam Store",
            icon_url="https://upload.wikimedia.org/"
                     "wikipedia/commons/thumb/8/83/Steam_icon_logo.svg/512px-Steam_icon_logo.svg.png"
        )
        embed.set_thumbnail(
            url=game_image
        )
        price = "Free"
        if game_data["release_date"]["coming_soon"]:
            price = f"Coming soon ({game_data['release_date']['date']})"
        else:
            release_date = game_data['release_date']['date']
            if release_date:
                embed.add_field(
                    name="Release date",
                    value=release_date,
                    inline=True
                )
        if not game_data["is_free"]:
            try:
                price = game_data["price_overview"]["final_formatted"]
            except KeyError:
                price = "¯\\\\_(ツ)\\_/¯"
        embed.add_field(
            name="Price",
            value=price,
            inline=True
        )
        if game_data.get("metacritic"):
            metacritic = f"{game_data['metacritic']['score']}"
            if game_data['metacritic'].get('url'):
                metacritic += f" [(link)]({game_data['metacritic']['url']})"
            embed.add_field(
                name="Metacritic",
                value=metacritic,
                inline=True
            )
        misc = ""
        if game_data.get("demos"):
            demos = game_data.get("demos")
            if len(demos) == 1:
                misc += f"[Demo found!](https://store.steampowered.com/app/{demos[0]['appid']})\n"
        platforms = game_data["platforms"]
        if platforms["mac"] and platforms["linux"]:
            misc += "macOS and Linux natively supported!\n"
        elif platforms["linux"]:
            misc += "Linux natively supported!\n"
        elif platforms["mac"]:
            misc += "macOS natively supported!\n"
        if misc:
            embed.add_field(
                name="Miscellaneous",
                value=misc,
                inline=True
            )
        if game_data['content_descriptors']['notes']:
            embed.add_field(
                name="Content descriptors",
                value=game_data['content_descriptors']['notes']
            )
        await ctx.reply(embed=embed)

    @commands.command(
        name='urban',
        description='Fetches a definition from Urban Dictionary, either by using the user\'s input, or by '
                    'getting a random word.',
        aliases=['ud', 'dictionary', 'definition'],
        brief='Searches for a definition on Urban Dictionary',
        usage='Sempiternal (or use with no args to fetch a random word)'
    )
    async def urban_command(self, ctx, *, query=None):
        if query:
            results = await ud_definition(query)
            word = results[0]
        else:
            word = await ud_random()
        embed = discord.Embed(
            title=f"Definition for *{word.word}*",
            description=f"{word.definition}",
            url=word.url
        ).set_footer(
            text=f"submitted by {word.author}, at {word.time.split('T')[0]}"
        )
        if word.example:
            if len(word.example) >= 1024:
                example = ''.join(
                    list(word.example)[:1021]) + '...'  # Apparently Discord upgraded their character limit.
            else:                                       # Haven't had much issues yet.
                example = word.example
            embed.add_field(
                name="Example",
                value=example
            )
        await ctx.reply(embed=embed)

    @commands.command(
        name='cat',
        description='Posts a random cat image.',
        aliases=["catto", "kitty", "fuckingkity"],
        brief='Posts a random cat image'
    )
    async def catto(self, ctx):
        await ctx.reply(await cat_image())  # FUCKING KITY :)

    @commands.command(
        name='dog',
        description='Posts a random dog image.',
        aliases=["doggy", "doggo"],
        brief='Posts a random dog image'
    )
    async def doggy(self, ctx):
        await ctx.reply(await dog_image())  # dogy :(

    @commands.command(
        name='never-obsolete',
        description='Posts a random image from the tumblr blog, https://never-obsolete.tumblr.com/. '
                    'Because technology is never obsolete.',
        aliases=["neverobsolete"],
        brief='images of old computers, operating systems, software and games'
    )
    async def never_obsolete_command(self, ctx):
        post = await random_tumblr_image('never-obsolete')

        embed = discord.Embed(url=post.url, timestamp=post.datetime).set_image(
            url=post.image).set_author(
            name="never obsolete",
            url=post.blogger.url,
            icon_url=post.blogger.avatar)

        embed.title = ext.format_html(post.description)

        await ctx.send(embed=embed)

    @commands.command(
        name='old-windows-icons',
        description='Posts a random image from the tumblr blog, https://oldwindowsicons.tumblr.com/. '
                    'They have a certain charm.',
        aliases=["oldwindowsicons", "windowsicons"],
        brief='images of old windows icons'
    )
    async def oldwindowsicons_command(self, ctx):
        post = await random_tumblr_image('oldwindowsicons')
        embed = discord.Embed(url=post.url, timestamp=post.datetime).set_image(
            url=post.image).set_author(
            name="old windows icons",
            url=post.blogger.url,
            icon_url=post.blogger.avatar)
        embed.title = ext.format_html(post.description)
        await ctx.send(embed=embed)


def setup(bot):
    bot.add_cog(Basic(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
