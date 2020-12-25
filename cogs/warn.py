import json
import os
import random
from datetime import datetime

import discord
from discord.ext import commands
from discord.ext.commands import has_permissions

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
            await ctx.send("Oh, REALLY now, huh? I do my best at maintaining this server and THIS is how you treat me? "
                           "Screw this..")
            return
        if user == ctx.author:
            await ctx.send("Why the heck would you warn yourself? You hate yourself THAT much?")
            return
        if user.bot == 1:
            await ctx.send("It's useless to warn a bot. Why would you even try.")
            return
        if user.guild_permissions.manage_messages:
            await ctx.send("The specified user has the \"Manage Messages\" permission "
                           "(or higher) inside the guild/server.")
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
                    'warns': 1,
                    1: ({
                        'warner': ctx.author.id,
                        'warner_name': ctx.author.name,
                        'reason': reason,
                        'channel': str(ctx.channel.id),
                        'datetime': dt_string
                        })
                })
                json.dump(warndata, warnfile, indent=2)
        else:
            # If the script made it this far, then the user has been warned
            warn_amount = warndata.get("warns")
            new_warn_amount = int(warn_amount)+1
            warndata["warns"] = new_warn_amount
            warndata["offender_name"] = user.name
            new_warn = ({
                'warner': ctx.author.id,
                'warner_name': ctx.author.name,
                'reason': reason,
                'channel': str(ctx.channel.id),
                'datetime': dt_string
            })
            warndata[new_warn_amount] = new_warn
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", newline="\n", encoding='utf-8'
                                     ), indent=2)
        discreason = reason.replace('**', '\\*\\*')
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
        await ctx.send(embed=embed)

    @warn_command.error
    async def warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await ctx.send(f'[{ctx.author.name}], you do not have the correct permissions to do so. '
                           f'*(commands.MissingPermissions error, action cancelled)*')
            return
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send(f"[{ctx.author.name}], you forgot to specify a user to warn. "
                               f"*(commands.MissingRequiredArgument error, action cancelled)*")
                return
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'reason':
                await ctx.send(f"[{ctx.author.name}], you forgot to specify a reason. "
                               f"*(commands.MissingRequiredArgument error, action cancelled)*")
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
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return

        # If the script made it this far, then the user has warns.
        warn_amount = warndata.get("warns")
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

        for x in range(1, warn_amount+1):
            with open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", newline="\n", encoding='utf-8') as warnfile:
                warndata = json.load(warnfile)

            warn_dict = warndata.get(str(x))
            warner_id = warn_dict.get('warner')
            warner_user = self.bot.get_user(id=warner_id)
            if warner_user is None:
                warner_name = warn_dict.get('warner_name')
            else:
                warner_name = self.bot.get_user(id=warner_id)
                
            warn_reason = warn_dict.get('reason')
            warn_channel = warn_dict.get('channel')
            warn_datetime = warn_dict.get('datetime')
            
            embed.add_field(
                name=f"Warn {x}",
                value=f"Warner: {warner_name} (<@{warner_id}>)\n"
                      f"Reason: {warn_reason}\n"
                      f"Channel: <#{warn_channel}>\n"
                      f"Date and Time: {warn_datetime}",
                inline=True
            )
        await ctx.send(
            content=None,
            embed=embed
        )

    @warns_command.error
    async def warns_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("Please mention someone to verify their warns.")
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('[{0.author.name}], you do not have the correct permissions to do so. '
                           '*(commands.MissingPermissions error, action cancelled)*'.format(ctx))
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
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return
        warn_amount = warndata.get('warns')
        specified_warn = warndata.get(warn)
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

        await ctx.send(content='Are you sure you want to remove this warn? (Reply with y or n)',
                       embed=confirmation_embed)
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            # do the whole removing process.
            if warn_amount == 1:   # Check if the user only has one warn.
                os.remove(f"data/servers/{ctx.guild.id}/warns/{user.id}.json")
                await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn removed.")
                return

            if warn != warn_amount:   # Check if the warn to remove was not the last warn.
                for x in range(int(warn), int(warn_amount)):
                    warndata[str(x)] = warndata[str(x+1)]
                    del warndata[str(x+1)]
                    json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w', newline="\n",
                                             encoding='utf-8'), indent=2)
                    await ctx.send(
                        f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn removed.")
                    return

            del warndata[str(warn)]
            warndata['warns'] = warn_amount - 1
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w', newline="\n",
                                     encoding='utf-8'), indent=2)
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn removed.")
            return
        elif reply in ('n', 'no', 'cancel'):
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what you want me to do. Action cancelled.")

    @remove_warn_command.error
    async def remove_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("Please mention someone to remove their warns.")
                return
            if error.param.name == 'warn':
                await ctx.send("You did not specify a warn ID to remove.")
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('[{0.author.name}], you do not have the correct permissions to do so. '
                           '*(commands.MissingPermissions error, action cancelled)*'.format(ctx))
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
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] does not have any warns.")
            return

        def check(ms):
            # Look for the message sent in the same channel where the command was used
            # As well as by the user who used the command.
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(content='What would you like to change the warn\'s reason to?')
        msg = await self.bot.wait_for('message', check=check)
        warn_new_reason = msg.content.lower()   # Set the title

        specified_warn = warndata.get(warn)
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

        await ctx.send(content='Are you sure you want to edit this warn like this? (Reply with y/yes or n/no)',
                       embed=confirmation_embed)

        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()   # Set the title
        if reply in ('y', 'yes', 'confirm'):
            specified_warn['reason'] = warn_new_reason
            json.dump(warndata, open(f"data/servers/{ctx.guild.id}/warns/{user.id}.json", 'w', newline="\n",
                                     encoding='utf-8'), indent=2)
            await ctx.send(f"[{ctx.author.name}], user [{user.name} ({user.id})] has gotten their warn edited.")
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what you want me to do. Action cancelled.")

    @edit_warn_command.error
    async def edit_warn_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("Please mention someone to remove their warns.")
                return
            if error.param.name == 'warn':
                await ctx.send("You did not specify a warn ID to remove.")
                return
        if isinstance(error, commands.MissingPermissions):
            await ctx.send('[{0.author.name}], you do not have the correct permissions to do so. '
                           '*(commands.MissingPermissions error, action cancelled)*'.format(ctx))
            return


def setup(bot):
    bot.add_cog(Warn(bot))
