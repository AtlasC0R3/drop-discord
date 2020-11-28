import json
import random

import discord
from discord.ext import commands
from discord.ext.commands import has_guild_permissions

from data.classes import write_server_config
from data.classes import get_server_config
from data.classes import get_entire_server_config


with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Configuration(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name="setprefix",
        description="Sets the bot's prefix for the server.",
        aliases=["prefix", "set_prefix"],
        brief='Sets a prefix for the current server'
    )
    @has_guild_permissions(manage_guild=True)
    async def setprefix_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if commandargs == '':
            await ctx.send('What would you like to set the prefix as for this server?')
            msg = await self.bot.wait_for('message', check=check)
            new_prefix = msg.content
        else:
            new_prefix = commandargs.replace(' ', '')

        if not len(new_prefix) == 1:
            await ctx.send("The prefix is longer than one character long. "
                           "You can only have one character as your prefix.\n"
                           f"*Requested prefix's length is {len(new_prefix)}*")
            return

        # Ask the user for confirmation
        await ctx.send(f"Are you sure you want to set `{new_prefix}` as your new server prefix?\n"
                       f"Example: `{new_prefix}help`")
        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            if get_server_config(ctx.guild.id, 'prefix', str) == new_prefix:
                await ctx.send("Hey wait a second, that's the same prefix as the current saved one! "
                               "*(Action cancelled. Not like it'd change anything if it weren't cancelled...)*")
                return
            write_server_config(ctx.guild.id, 'prefix', new_prefix)
            await ctx.send("Successfully changed server prefix.")
            write_server_config(ctx.guild.id, 'asked_prefix', [])
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what that means. *Action cancelled.*")

    @setprefix_command.error
    async def setprefix_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="toggle_inactivity",
        description="Toggles the bot's inactivity function for this server.",
        aliases=["toggleinactivity"],
        brief='Toggles the inactivity messages'
    )
    @has_guild_permissions(manage_guild=True)
    async def toggleinactivity_command(self, ctx):
        if get_server_config(ctx.guild.id, 'inactivity_func', bool):
            write_server_config(ctx.guild.id, 'inactivity_func', False)
            await ctx.send("Success, inactivity function is now turned off.")
        else:
            write_server_config(ctx.guild.id, 'inactivity_func', True)
            await ctx.send("Success, inactivity function is now turned on.")

    @toggleinactivity_command.error
    async def toggleinactivity_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="banword",
        description="If the bot hears this word, it will automatically delete it (and send a warn if told to do so)",
        aliases=["nonoword"],
        brief="Ban a certain word"
    )
    @has_guild_permissions(manage_guild=True)
    async def banword_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]
        if commandargs == '':
            await ctx.send('Which word would you like to ban?')
            msg = await self.bot.wait_for('message', check=check)
            nonoword = msg.content
        else:
            nonoword = commandargs.replace(' ', '')
        nonowords = get_server_config(ctx.guild.id, 'no_no_words', list)

        if nonoword in nonowords:
            # it's already in, we have to delete it
            new_nonowords = [x for x in nonowords if x != nonoword]
            write_server_config(ctx.guild.id, 'no_no_words', new_nonowords)
            await ctx.send("Success, this word has been unbanned.")
        else:
            # it's not in, we have to add it
            nonowords.append(nonoword)
            write_server_config(ctx.guild.id, 'no_no_words', nonowords)
            await ctx.send("Success, this word has been banned.")

    @commands.command(
        name="inactivitychannel",
        description="Adds/removes channels to the bot's inactivity function.",
        aliases=["addinactivitychannel", "addchannel"],
        brief='I\'m bad at explaining things...'
    )
    @has_guild_permissions(manage_guild=True)
    async def inactivitychannel_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if commandargs == '':
            await ctx.send('What channel would you like to toggle?')
            msg = await self.bot.wait_for('message', check=check)
            new_channel = msg.content
        else:
            new_channel = commandargs

        replace = {' ': '',
                   '<': '',
                   '#': '',
                   '>': ''}
        for key, value in replace.items():
            new_channel = new_channel.replace(key, value)

        if new_channel.isdigit():
            channel = ctx.guild.get_channel(int(new_channel))
            if channel is None:
                await ctx.send("Uh oh, I could not get the channel you meant. Please try again. "
                               "If it still fails, please try directly inserting the channel's ID. *Action cancelled.*")
                return
        else:
            channel = discord.utils.get(self.bot.get_all_channels(), guild=ctx.guild, name=new_channel)
            if channel is None:
                await ctx.send("Whoops, I couldn't find the channel you meant. "
                               "Please try again by directly mentioning the channel you mean. *Action cancelled.*")
                return

        # Ask the user for confirmation
        if channel.id in get_server_config(ctx.guild.id, 'inactivity_channels', list):
            await ctx.send(f"Are you sure you want to remove <#{channel.id}> from the inactivity channels?")
            remove = True
        else:
            await ctx.send(f"Are you sure you want to add <#{channel.id}> to the inactivity channels?")
            remove = False
        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            if remove:
                new_list = [x for x in get_server_config(ctx.guild.id, 'inactivity_channels', list) if x != channel.id]
                write_server_config(ctx.guild.id, 'inactivity_channels', new_list)
                await ctx.send(f"Successfully removed <#{channel.id}> from the inactivity channels.")
                return
            else:
                new_list = get_server_config(ctx.guild.id, 'inactivity_channels', list)
                new_list.append(channel.id)
                write_server_config(ctx.guild.id, 'inactivity_channels', new_list)
                await ctx.send(f"Successfully added <#{channel.id}> to the inactivity channels.")
                return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what that means. *Action cancelled.*")

    @inactivitychannel_command.error
    async def inactivitychannel_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="muted_role",
        description="Sets the muted role, for the mute commands.",
        aliases=["muterole"],
        brief='Configure the muted role for the bot'
    )
    @has_guild_permissions(manage_guild=True)
    async def mutedrole_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if commandargs == '':
            await ctx.send('Which role would you like to set the mute role as?')
            msg = await self.bot.wait_for('message', check=check)
            new_role = msg.content
        else:
            new_role = commandargs

        replace = {' ': '',
                   '<': '',
                   '@': '',
                   '&': '',
                   '>': ''}
        for key, value in replace.items():
            new_role = new_role.replace(key, value)

        if new_role.isdigit():
            role = ctx.guild.get_role(int(new_role))
            if role is None:
                await ctx.send("Uh oh, I could not get the role you meant. Please try again. "
                               "If it still fails, please try directly inserting the role's ID. *Action cancelled.*")
                return
        else:
            role = discord.utils.get(ctx.guild.roles, name=new_role)
            if role is None:
                await ctx.send("Whoops, I couldn't find the role you meant. "
                               "Please try again by directly mentioning the role you mean. *Action cancelled.*")
                return

        # Checks if role is already the one that's already defined. If not, ask for confirmation
        if role.id == get_server_config(ctx.guild.id, 'mute_role', int):
            await ctx.send("Hey wait a second, that's the role that has already been defined as the mute role! "
                           "*Action cancelled. I mean, it wouldn't change anything if it weren't cancelled...*")
            return
        else:
            await ctx.send(f"Are you sure you want to set {role.name} as the mute role?")
        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            write_server_config(ctx.guild.id, 'mute_role', role.id)
            await ctx.send(f"Successfully set {role.name} as the muted role")
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what that means. *Action cancelled.*")

    @mutedrole_command.error
    async def mutedrole_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="configinfo",
        description="Sends the current server's entire config file.",
        brief='See the exact config for this server'
    )
    @has_guild_permissions(manage_guild=True)
    async def configinfo_command(self, ctx):
        embed = discord.Embed(
            title=f'Config for "{ctx.guild.name}"',
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=ctx.guild.icon_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        server_cfg = get_entire_server_config(ctx.guild.id)
        for key, value in server_cfg.items():
            if key == 'no_no_words':
                value = f'||{value}||'
            embed.add_field(
                name=key,
                value=value,
                inline=True
            )
        await ctx.send(embed=embed)

    @configinfo_command.error
    async def configinfo_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="anonymouslogs",
        description="Enables/disables the bot to automatically send error logs to the bot host.\n"
                    "May help bot development and bug fixing, however could also raise privacy concern among users.",
        aliases=["toggle_errorlogs", "toggle_anonymouslogs", "togglelogs"],
        brief='Toggle the anonymous error logs'
    )
    @has_guild_permissions(manage_guild=True)
    async def anonymouslogs_command(self, ctx):
        if get_server_config(ctx.guild.id, 'share_error_logs', bool):
            write_server_config(ctx.guild.id, 'inactivity_func', False)
            await ctx.send("Success, anonymous error logs will no longer be automatically sent to the bot host.")
        else:
            write_server_config(ctx.guild.id, 'share_error_logs', True)
            await ctx.send("Success, anonymous error logs will now be automatically sent to the bot host.")

    @anonymouslogs_command.error  # Ha! An error handler for an error handling command. The irony.
    async def anonymouslogs_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="toggle_inactivity",
        description="Toggles the bot's inactivity function for this server.",
        aliases=["toggleinactivity"],
        brief='Toggles the inactivity messages'
    )
    @has_guild_permissions(manage_guild=True)
    async def toggleinactivity_command(self, ctx):
        if get_server_config(ctx.guild.id, 'inactivity_func', bool):
            write_server_config(ctx.guild.id, 'inactivity_func', False)
            await ctx.send("Success, inactivity function is now turned off.")
        else:
            write_server_config(ctx.guild.id, 'inactivity_func', True)
            await ctx.send("Success, inactivity function is now turned on.")

    @toggleinactivity_command.error
    async def toggleinactivity_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return

    @commands.command(
        name="togglecommand",
        description="Disables/enables commands. This can be used to disable commands you don't want in your server.\n"
                    "Additionally, this disables the ability to see them in the help command.",
        aliases=["togglecmd"],
        brief='Toggles a command'
    )
    @has_guild_permissions(manage_guild=True)
    async def disablecmd_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]
        if commandargs == '':
            await ctx.send('Which command would you like to disable?')
            msg = await self.bot.wait_for('message', check=check)
            togglethingy = msg.content.lower()
        else:
            togglethingy = commandargs.replace(' ', '').lower()
        disabled_commands = get_server_config(ctx.guild.id, 'disabled_commands', list)
        cmdthingy = self.bot.get_command(togglethingy)
        if not cmdthingy:
            await ctx.send("I could not find that command. *Action cancelled.*")
            return
        if togglethingy == 'help':
            await ctx.send("Umm, are you *sure* you want to toggle the help command?")
            replymsg = await self.bot.wait_for('message', check=check)
            reply = replymsg.content.lower()

            if reply in ('y', 'yes', 'confirm'):
                pass
            elif reply in ('n', 'no', 'cancel', 'flanksteak'):
                await ctx.send("Alright, action cancelled.")
                return
            else:
                await ctx.send("I have no idea what that means. *Action cancelled.*")
                return
        if togglethingy in disabled_commands:
            new_commands = [x for x in disabled_commands if x != togglethingy]
            write_server_config(ctx.guild.id, 'disabled_commands', new_commands)
            await ctx.send("Success, this command is now enabled.")
        else:
            disabled_commands.append(togglethingy)
            write_server_config(ctx.guild.id, 'disabled_commands', disabled_commands)
            await ctx.send("Success, this command is now disabled.")

    @disablecmd_command.error
    async def disablecmd_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(f"{ctx.author.name}, you don't have the permissions to do that.\n"
                           f"*({error} Action cancelled)*")
            return


def setup(bot):
    bot.add_cog(Configuration(bot))
