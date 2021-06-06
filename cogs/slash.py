from discord.ext import commands
from discord_slash import cog_ext, SlashContext
from data.extdata import get_listening_to, get_language_str, get_config_parameter
from drop.basic import get_lyrics, get_artist, search
from drop.moderation import get_warns
from lyricsgenius.genius import Song
import re


class Slash(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @cog_ext.cog_slash(name="lyrics", description="Return lyrics from a song. If your Discord activity is currently "
                                                  "playing a song, args are optional.")
    async def lyrics_slash(self, ctx: SlashContext, title="", artist=""):
        await ctx.defer(hidden=True)
        if title and artist:
            args = [title, artist]
        elif (not title) and artist:
            args = artist
        elif (not artist) and title:
            await ctx.send("How the hell do you want me to make this work? I need a title **and** an artist!",
                           hidden=True)
            return
        else:
            # check if user playing something on spotefiye
            # discord when will you add support for tidal /s
            if not ctx.guild:
                await ctx.send("I can't retrieve your user activity inside private messages, "
                               "so you'll have to manually insert them.",
                               hidden=True)
                return
            author = ctx.guild.get_member(ctx.author.id)
            args = get_listening_to(author.activities)
        if not args:
            await ctx.send(content="Could not find the currently playing song in your Discord activity, "
                                   "meaning you'll have to manually put the title and song.", hidden=True)
            return
        if type(args) is list:
            # search for song
            song = re.compile(r' \(.*?\)').sub('', args[0])
            artist = args[-1]
            lyrics = get_lyrics(artist=artist, title=song)
            if type(lyrics) is Song:
                # that is Genius.
                obtained_from = 'Genius'
                title = lyrics.title
                artist = lyrics.artist
                url = lyrics.url
            else:
                obtained_from = 'something'
                title = "Nothing"
                artist = "No One"
                url = ""
            try:
                lyric_str = lyrics.lyrics
            except AttributeError:
                lyric_str = get_language_str(ctx.guild.id, 17)
                obtained_from = 'common sense'
            song_by_artist = get_language_str(ctx.guild.id, 20).format(title, artist)
            footer = f"*obtained using {obtained_from}*\n{url}"
            remaining_characters = 2000 - (len(song_by_artist) + len(footer) + 16)   # added the 16 in case full_content
            if len(lyric_str) >= remaining_characters:                               # would add any more characters.
                lyric_str = ''.join(list(lyric_str)[:remaining_characters]) + '...'  # and for that right here.
            full_content = f"{song_by_artist}\n" \
                           f"```{lyric_str}```" \
                           f"\n{footer}"
            await ctx.send(content=full_content, hidden=True)
        else:
            # search for artist
            obtained = get_artist(args)
            artist = obtained[1]
            service = obtained[0]
            if not artist:
                await ctx.send(get_language_str(ctx.guild.id, 18), hidden=True)
                return
            if service == 'Genius':
                artist_name = artist[0]
                title = f'Popular songs by *{artist_name}*'
            elif service == 'MetroLyrics':
                title = f'Random songs by *{artist[0]}*'
                artist = obtained[1]
            else:
                title = 'Some songs.'
            lyric_portion = ""
            footer = f'obtained using {service}'
            for song in artist[1]:
                song_name = song[0]
                lyrics = '\n'.join(song[1])
                url = song[2]
                if not lyrics:
                    lyrics = get_language_str(ctx.guild.id, 17)
                else:
                    if url:
                        lyrics = '```' + lyrics + f'```\n<{url}>'
                    else:
                        lyrics = '```' + lyrics + '\n...```'
                lyric_portion = lyric_portion + f"\n**{song_name}**\n{lyrics}\n"
            content = f"**{title}**\n{lyric_portion}\n*{footer}*"
            await ctx.send(content=content, hidden=True)

    @cog_ext.cog_slash(name="search", description="Does a DuckDuckGo search.")
    async def search_slash(self, ctx: SlashContext, query: str):
        await ctx.defer(hidden=True)
        response = search(query)
        if response is not None:
            title = response['title']
            description = response['description']
            url = response['url']
            source = response['source']
            fields = ""
            for field in response['fields']:
                name = field['name']
                value = field['value']
                fields = fields + f'**{name}**: {value}\n'
            content = f"**{title}** *(<{url}>)*\n{description}\n*-{source}*\n\n{fields}"
            await ctx.send(content=content, hidden=True)
        else:
            await ctx.send(get_language_str(ctx.guild.id, 122), hidden=True)

    @cog_ext.cog_slash(name="warns", description="Returns the author's warns.")
    async def warns_slash(self, ctx: SlashContext):
        await ctx.defer(hidden=True)
        warn_data = get_warns(ctx.guild.id, ctx.author.id)
        if not warn_data:
            await ctx.send(get_language_str(ctx.guild.id, 114), hidden=True)
            return
        warns = warn_data.get("warns")
        warns_str = ""
        for index, warn_thing in enumerate(warns):
            warner_id = warn_thing.get('warner')
            warner_user = self.bot.get_user(id=warner_id)
            if warner_user is None:
                warner_name = warn_thing.get('warner_name')
            else:
                warner_name = self.bot.get_user(id=warner_id)

            warn_reason = warn_thing.get('reason')
            warn_channel = warn_thing.get('channel')
            warn_datetime = warn_thing.get('datetime')

            warns_str = warns_str + f"```{warn_reason}```" \
                                    f"*<#{warn_channel}>, {warn_datetime}, " \
                                    f"warned by {warner_name} (<@{warner_id}>), warn {index + 1}*\n\n"
        await ctx.send(warns_str, hidden=True)


def setup(bot):
    if get_config_parameter('slash_commands', bool):
        bot.add_cog(Slash(bot))
