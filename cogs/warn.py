import json
import os
import random
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions
from data.extdata import get_language_str

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
        dt_string = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        if not os.path.exists("data/servers/" + str(ctx.guild.id) + "/warns/"):
            os.makedirs("data/servers/" + str(ctx.guild.id) + "/warns/")
            # Checks if the folder for the guild exists. If it doesn't, create it.
        try:
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", newline="\n", encoding='utf-8') as warnfile:
                warndata = json.load(warnfile)
            # See if the user has been warned
        except FileNotFoundError:
            # User has not been warned yet
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w+', newline="\n", encoding='utf-8') as \
                    warnfile:
                warndata = ({
                    'offender_name': user.name,
                    'warns': [
                        {
                            'warner': ctx.author.id,
                            'warner_name': ctx.author.name,
                            'reason': reason,
                            'channel': str(ctx.channel.id),
                            'datetime': dt_string
                        }
                    ]
                })
                json.dump(warndata, warnfile, indent=2)
        else:
            # If the script made it this far, then the user has been warned
            warndata["offender_name"] = user.name
            new_warn = ({
                'warner': ctx.author.id,
                'warner_name': ctx.author.name,
                'reason': reason,
                'channel': str(ctx.channel.id),
                'datetime': dt_string
            })
            warndata["warns"].append(new_warn)
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", "w+", newline="\n",
                                     encoding='utf-8'), indent=2)
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
            await ctx.reply(f'[{ctx.author.name}], you do not have the correct permissions to do so. '
                            f'*(commands.MissingPermissions error, action cancelled)*')
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
        try:
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'r', newline="\n", encoding='utf-8') as \
                    warnfile:
                warndata = json.load(warnfile)
            # See if the user has been warned
        except FileNotFoundError:
            # User does not have any warns.
            await ctx.reply(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
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

        for index, warn in enumerate(warns):
            warner_id = warn.get('warner')
            warner_user = self.bot.get_user(id=warner_id)
            if warner_user is None:
                warner_name = warn.get('warner_name')
            else:
                warner_name = self.bot.get_user(id=warner_id)
                
            warn_reason = warn.get('reason')
            warn_channel = warn.get('channel')
            warn_datetime = warn.get('datetime')
            
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
    async def remove_warn_command(self, ctx, user: discord.Member, *, warn: str):
        try:
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", newline="\n", encoding='utf-8') as warnfile:
                warndata = json.load(warnfile)
            # See if the user has been warned
        except FileNotFoundError:
            # User does not have any warns.
            await ctx.reply(get_language_str(ctx.guild.id, 114))
            return
        warns = warndata.get('warns')
        warnindex = int(warn) - 1
        if warnindex < 0:
            await ctx.reply(get_language_str(ctx.guild.id, 115))
            return
        specified_warn = warns[warnindex]
        warn_warner = specified_warn.get('warner')
        warn_reason = specified_warn.get('reason')
        warn_channel = specified_warn.get('channel')
        warn_datetime = specified_warn.get('datetime')
        warn_warner_name = self.bot.get_user(id=warn_warner)

        confirmation_embed = discord.Embed(
            title=f'{user.name}\'s warn number {warn}',
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

        await ctx.send(content=get_language_str(ctx.guild.id, get_language_str(ctx.guild.id, 116)) + ' (y or n)',
                       embed=confirmation_embed)
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            # do the whole removing process.
            warns = [x for x in warns if x != warns[warnindex]]
            warndata["warns"] = warns
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w', newline="\n",
                                     encoding='utf-8'), indent=2)
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
    async def edit_warn_command(self, ctx, user: discord.Member, *, warn: str):
        try:
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", newline="\n", encoding='utf-8') as warnfile:
                warndata = json.load(warnfile)
            # See if the user has been warned
        except FileNotFoundError:
            # User does not have any warns.
            await ctx.reply(get_language_str(ctx.guild.id, 114))
            return

        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(content=get_language_str(ctx.guild.id, 119))
        msg = await self.bot.wait_for('message', check=check)
        warn_new_reason = msg.content.lower()   # Set the title

        warns = warndata.get("warns")
        warnindex = int(warn) - 1
        if warnindex < 0:
            await ctx.reply(get_language_str(ctx.guild.id, 115))
            return
        specified_warn = warns[warnindex]
        warn_warner = specified_warn.get('warner')
        warn_channel = specified_warn.get('channel')
        warn_datetime = specified_warn.get('datetime')
        warn_warner_name = self.bot.get_user(id=warn_warner)

        confirmation_embed = discord.Embed(
            title=f'{user.name}\'s warn number {warn}',
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

        await ctx.send(content=get_language_str(ctx.guild.id, get_language_str(ctx.guild.id, 120)) + ' (y/n)',
                       embed=confirmation_embed)

        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            specified_warn['reason'] = warn_new_reason
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w', newline="\n",
                                     encoding='utf-8'), indent=2)
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
