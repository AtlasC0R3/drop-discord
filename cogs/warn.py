import random

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.extdata import get_language_str

from drop.moderation import *

# These color constants are taken from discord.js library
with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Warn(commands.Cog):
    """
    All of the commands for warning someone.
    """
    
    def __init__(self, bot):
        self.bot = bot
        
    # Define a new command
    @commands.command(
        name='warn',
        description='Warns a user for a specific reason, for example, breaking rules, or simply being an idiot',
        usage='<@offender> called my mommy a fat :((((((( cri',
        brief='Warns a user'
    )
    @has_permissions(manage_messages=True)
    async def warn_command(self, ctx, user: discord.Member, *, reason: str):
        if user.id == self.bot.user.id:
            await ctx.reply(get_language_str(ctx.guild.id, 73))
            return
        if user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 74))
            return
        if user.bot == 1:
            await ctx.reply(get_language_str(ctx.guild.id, 110))
            return
        if user.guild_permissions.manage_messages:
            await ctx.reply(get_language_str(ctx.guild.id, 75))
            return
        warn(ctx.guild.id, user.id, user.name, ctx.author.id, ctx.author.name, ctx.message.channel.id, reason)
        discreason = reason.replace('*', '\\*')
        embed = discord.Embed(
            title="User warned",
            description=f"User: **{user}**\n"
                        f"Reason: **{discreason}**\n"
                        f"Warned by: **{ctx.author}**",
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.reply(embed=embed)

    @warn_command.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 192))
            return
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 111).format(ctx.author.name))
                return
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'reason':
                await ctx.reply(get_language_str(ctx.guild.id, 112).format(ctx.author.name))
                return

    @commands.command(
        name='warns',
        description='See all the warns a user has',
        usage='<@offender>',
        aliases=['warnings'],
        brief='Check a user\'s warns'
    )
    @has_permissions(manage_messages=True)
    async def warns_command(self, ctx, *, user: discord.Member):
        warndata = get_warns(ctx.guild.id, user.id)
        if not warndata:
            await ctx.reply(get_language_str(ctx.guild.id, 114))
            return

        # If the script made it this far, then the user has warns.
        warns = warndata.get("warns")
        warn_amount = len(warns)
        if warn_amount == 1:
            warns_word = "warn"
        else:
            warns_word = "warns"

        username = user.name

        embed = discord.Embed(
            title=f"{username}'s warns",
            description=f"They have {warn_amount} {warns_word}.",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

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
            
            embed.add_field(
                name=f"Warn {index + 1}",
                value=f"Warner: {warner_name} (<@{warner_id}>)\n"
                      f"Reason: {warn_reason}\n"
                      f"Channel: <#{warn_channel}>\n"
                      f"Date and Time: {warn_datetime}",
                inline=True
            )
        await ctx.reply(
            content=None,
            embed=embed
        )
        # too lazy to translate this command, freaking hell

    @warns_command.error
    async def warns_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 113))
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name='remove_warn',
        description='Removes a specific warn from a specific user.',
        usage='@user 2',
        aliases=['removewarn', 'clearwarn'],
        brief='Remove a warn from a user'
    )
    @has_permissions(manage_messages=True)
    async def remove_warn_command(self, ctx, user: discord.Member, *, warn_index: int):
        warn_index = int(warn_index) - 1

        specified_warn = get_warn(ctx.guild.id, user.id, warn_index)
        warn_warner = specified_warn.get('warner')
        warn_reason = specified_warn.get('reason')
        warn_channel = specified_warn.get('channel')
        warn_datetime = specified_warn.get('datetime')
        warn_warner_name = self.bot.get_user(id=warn_warner)

        confirmation_embed = discord.Embed(
            title=f'{user.name}\'s warn number {warn_index}',
            description=f'Warner: {warn_warner_name}\n'
                        f'Reason: {warn_reason}\n'
                        f'Channel: <#{warn_channel}>\n'
                        f'Date and Time: {warn_datetime}',
            color=random.choice(color_list),
        )
        confirmation_embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(content=get_language_str(ctx.guild.id, 116) + ' (y or n)',
                       embed=confirmation_embed)
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            remove_warn(ctx.guild.id, user.id, warn_index)
            await ctx.reply(get_language_str(ctx.guild.id, 117))
            return
        elif reply in ('n', 'no', 'cancel'):
            await ctx.send(get_language_str(ctx.guild.id, 26))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 27))

    @remove_warn_command.error
    async def remove_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 118))
                return
            if error.param.name == 'warn':
                await ctx.reply(get_language_str(ctx.guild.id, 115))
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name='edit_warn',
        description='Edits a specific warn reason from a specific user.',
        usage='@user 2',
        aliases=['editwarn', 'changewarn'],
        brief='Edit a user\'s warn'
    )
    @has_permissions(manage_messages=True)
    async def edit_warn_command(self, ctx, user: discord.Member, *, warn_index: str):
        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        warnindex = int(warn_index) - 1
        if warnindex < 0:
            await ctx.reply(get_language_str(ctx.guild.id, 115))
            return
        try:
            specified_warn = get_warn(ctx.guild.id, user.id, warnindex)
        except IndexError:
            await ctx.reply(get_language_str(ctx.guild.id, 115))
            return
        await ctx.send(content=get_language_str(ctx.guild.id, 119))
        msg = await self.bot.wait_for('message', check=check)
        warn_new_reason = msg.content

        warn_warner = specified_warn.get('warner')
        warn_channel = specified_warn.get('channel')
        warn_datetime = specified_warn.get('datetime')
        warn_warner_name = self.bot.get_user(id=warn_warner)

        confirmation_embed = discord.Embed(
            title=f'{user.name}\'s warn number {warn_index}',
            description=f'Warner: {warn_warner_name}\n'
                        f'Reason: {warn_new_reason}\n'
                        f'Channel: <#{warn_channel}>\n'
                        f'Date and Time: {warn_datetime}',
            color=random.choice(color_list),
        )
        confirmation_embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        await ctx.send(content=get_language_str(ctx.guild.id, 120) + ' (y/n)',
                       embed=confirmation_embed)

        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            edit_warn(ctx.guild.id, user.id, int(warnindex), warn_new_reason)
            await ctx.reply(get_language_str(ctx.guild.id, 121))
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send(get_language_str(ctx.guild.id, 26))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 27))

    @edit_warn_command.error
    async def edit_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 118))
                return
            if error.param.name == 'warn':
                await ctx.reply(get_language_str(ctx.guild.id, 115))
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return


def setup(bot):
    bot.add_cog(Warn(bot))
