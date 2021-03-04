import json
import random
from datetime import datetime
import shutil

import discord
from discord.ext import commands, tasks
from discord.ext.commands import has_guild_permissions

import parsedatetime

from data.extdata import write_server_config, get_server_config, get_entire_server_config, get_language_str, \
    get_all_languages

cal = parsedatetime.Calendar()

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Configuration(commands.Cog):
    """
    A set of configuration commands, to configure the bot correctly for this server.
    """

    def __init__(self, bot):
        self.bot = bot
        self.data_clearer.start()

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

        command_msg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        command_args = command_msg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if command_args == '':
            await ctx.reply(get_language_str(ctx.guild.id, 21))
            msg = await self.bot.wait_for('message', check=check)
            new_prefix = msg.content
        else:
            new_prefix = command_args.replace(' ', '')

        if not len(new_prefix) == 1:
            await ctx.reply(get_language_str(ctx.guild.id, 22).format(len(new_prefix)))
            return

        # Ask the user for confirmation
        await ctx.send(get_language_str(ctx.guild.id, 23).format(new_prefix))
        reply_msg = await self.bot.wait_for('message', check=check)
        reply = reply_msg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            if get_server_config(ctx.guild.id, 'prefix', str) == new_prefix:
                await ctx.send(get_language_str(ctx.guild.id, 24))
                return
            write_server_config(ctx.guild.id, 'prefix', new_prefix)
            await ctx.reply(get_language_str(ctx.guild.id, 25))
            write_server_config(ctx.guild.id, 'asked_prefix', [])
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send(get_language_str(ctx.guild.id, 26))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 27))

    @setprefix_command.error
    async def setprefix_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
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
            await ctx.reply(get_language_str(ctx.guild.id, 29))
        else:
            write_server_config(ctx.guild.id, 'inactivity_func', True)
            await ctx.reply(get_language_str(ctx.guild.id, 30))

    @toggleinactivity_command.error
    async def toggleinactivity_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name="banword",
        description="If the bot hears this word, it will automatically delete it",
        aliases=["nonoword"],
        brief="Ban a certain word"
    )
    @has_guild_permissions(manage_guild=True)
    async def banword_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        command_msg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        command_args = command_msg[len(prefix_used) + len(alias_used):]
        if command_args == '':
            await ctx.send(get_language_str(ctx.guild.id, 31))
            msg = await self.bot.wait_for('message', check=check)
            nonoword = msg.content
        else:
            nonoword = command_args.replace(' ', '')
        no_no_words = get_server_config(ctx.guild.id, 'no_no_words', list)

        if nonoword in no_no_words:
            # it's already in, we have to delete it
            new_nonowords = [x for x in no_no_words if x != nonoword]
            write_server_config(ctx.guild.id, 'no_no_words', new_nonowords)
            await ctx.reply(get_language_str(ctx.guild.id, 32))
        else:
            # it's not in, we have to add it
            no_no_words.append(nonoword)
            write_server_config(ctx.guild.id, 'no_no_words', no_no_words)
            await ctx.reply(get_language_str(ctx.guild.id, 33))

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

        command_msg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        command_args = command_msg[len(prefix_used) + len(alias_used):]

        # Next, we check if the user actually passed some text
        if command_args == '':
            await ctx.send(get_language_str(ctx.guild.id, 34))
            msg = await self.bot.wait_for('message', check=check)
            new_channel = msg.content
        else:
            new_channel = command_args

        replace = {' ': '',
                   '<': '',
                   '#': '',
                   '>': ''}
        for key, value in replace.items():
            new_channel = new_channel.replace(key, value)

        if new_channel.isdigit():
            channel = ctx.guild.get_channel(int(new_channel))
            if channel is None:
                await ctx.reply(get_language_str(ctx.guild.id, 35))
                return
        else:
            channel = discord.utils.get(self.bot.get_all_channels(), guild=ctx.guild, name=new_channel)
            if channel is None:
                await ctx.reply(get_language_str(ctx.guild.id, 36))
                return

        # Ask the user for confirmation
        if channel.id in get_server_config(ctx.guild.id, 'inactivity_channels', list):
            await ctx.send(get_language_str(ctx.guild.id, 37).format(channel.id))
            remove = True
        else:
            await ctx.send(get_language_str(ctx.guild.id, 38).format(channel.id))
            remove = False
        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            if remove:
                new_list = [x for x in get_server_config(ctx.guild.id, 'inactivity_channels', list) if x != channel.id]
                write_server_config(ctx.guild.id, 'inactivity_channels', new_list)
                await ctx.reply(get_language_str(ctx.guild.id, 39).format(channel.id))
                return
            else:
                new_list = get_server_config(ctx.guild.id, 'inactivity_channels', list)
                new_list.append(channel.id)
                write_server_config(ctx.guild.id, 'inactivity_channels', new_list)
                await ctx.reply(get_language_str(ctx.guild.id, 40).format(channel.id))
                return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send(get_language_str(ctx.guild.id, 26))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 27))

    @inactivitychannel_command.error
    async def inactivitychannel_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
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
            await ctx.send(get_language_str(ctx.guild.id, 41))
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
                await ctx.reply(get_language_str(ctx.guild.id, 42))
                return
        else:
            role = discord.utils.get(ctx.guild.roles, name=new_role)
            if role is None:
                await ctx.reply(get_language_str(ctx.guild.id, 43))
                return

        # Checks if role is already the one that's already defined. If not, ask for confirmation
        if role.id == get_server_config(ctx.guild.id, 'mute_role', int):
            await ctx.send(get_language_str(ctx.guild.id, 44))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 45).format(role.name))
        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()

        if reply in ('y', 'yes', 'confirm'):
            write_server_config(ctx.guild.id, 'mute_role', role.id)
            await ctx.reply(get_language_str(ctx.guild.id, 46).format(role.name))
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send(get_language_str(ctx.guild.id, 26))
            return
        else:
            await ctx.send(get_language_str(ctx.guild.id, 27))

    @mutedrole_command.error
    async def mutedrole_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
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
        await ctx.reply(embed=embed)

    @configinfo_command.error
    async def configinfo_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.repy(f"{ctx.author.name}, you don't have the permissions to do that.\n"
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
            await ctx.reply(get_language_str(ctx.guild.id, 47))
        else:
            write_server_config(ctx.guild.id, 'share_error_logs', True)
            await ctx.reply(get_language_str(ctx.guild.id, 48))

    @anonymouslogs_command.error  # Ha! An error handler for an error handling command. The irony.
    async def anonymouslogs_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
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
            await ctx.reply(get_language_str(ctx.guild.id, 49))
        else:
            write_server_config(ctx.guild.id, 'inactivity_func', True)
            await ctx.reply(get_language_str(ctx.guild.id, 50))

    @toggleinactivity_command.error
    async def toggleinactivity_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name="toggle_tableflip",
        description="Toggles the bot's tableflip reaction for this server.",
        aliases=["toggletableflip", "toggleflip"],
        brief='Toggles the tableflip reactions'
    )
    @has_guild_permissions(manage_guild=True)
    async def toggleflip_command(self, ctx):
        if get_server_config(ctx.guild.id, 'tableflip', bool):
            write_server_config(ctx.guild.id, 'tableflip', False)
            await ctx.reply(get_language_str(ctx.guild.id, 51))
        else:
            write_server_config(ctx.guild.id, 'tableflip', True)
            await ctx.reply(get_language_str(ctx.guild.id, 52))

    @toggleflip_command.error
    async def toggleflip_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
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
            await ctx.send(get_language_str(ctx.guild.id, 53))
            msg = await self.bot.wait_for('message', check=check)
            togglethingy = msg.content.lower()
        else:
            togglethingy = commandargs.replace(' ', '').lower()
        disabled_commands = get_server_config(ctx.guild.id, 'disabled_commands', list)
        cmdthingy = self.bot.get_command(togglethingy)
        if not cmdthingy:
            await ctx.reply(get_language_str(ctx.guild.id, 54))
            return
        if togglethingy == 'help':
            await ctx.send(get_language_str(ctx.guild.id, 55))
            replymsg = await self.bot.wait_for('message', check=check)
            reply = replymsg.content.lower()

            if reply in ('y', 'yes', 'confirm'):
                pass
            elif reply in ('n', 'no', 'cancel', 'flanksteak'):
                await ctx.send(get_language_str(ctx.guild.id, 26))
                return
            else:
                await ctx.send(get_language_str(ctx.guild.id, 27))
                return
        if togglethingy in disabled_commands:
            new_commands = [x for x in disabled_commands if x != togglethingy]
            write_server_config(ctx.guild.id, 'disabled_commands', new_commands)
            await ctx.reply(get_language_str(ctx.guild.id, 56))
        else:
            disabled_commands.append(togglethingy)
            write_server_config(ctx.guild.id, 'disabled_commands', disabled_commands)
            await ctx.reply(get_language_str(ctx.guild.id, 57))

    @disablecmd_command.error
    async def disablecmd_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.send(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name="togglecog",
        description="Disables/enables commands. This can be used to disable commands you don't want in your server.\n"
                    "Additionally, this disables the ability to see them in the help command.",
        aliases=["togglecategory"],
        brief='Toggles a category'
    )
    @has_guild_permissions(manage_guild=True)
    async def disablecog_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        commandmsg = ctx.message.content
        prefix_used = ctx.prefix
        alias_used = ctx.invoked_with
        commandargs = commandmsg[len(prefix_used) + len(alias_used):]
        if commandargs == '':
            await ctx.send(get_language_str(ctx.guild.id, 58))
            msg = await self.bot.wait_for('message', check=check)
            togglethingy = msg.content
        else:
            togglethingy = commandargs.replace(' ', '')
        disabled_cogs = get_server_config(ctx.guild.id, 'disabled_cogs', list)
        cmdthingy = self.bot.get_cog(togglethingy)
        if not cmdthingy:
            await ctx.reply(get_language_str(ctx.guild.id, 59))
            return

        if togglethingy in disabled_cogs:
            new_cogs = [x for x in disabled_cogs if x != togglethingy]
            write_server_config(ctx.guild.id, 'disabled_cogs', new_cogs)
            await ctx.reply(get_language_str(ctx.guild.id, 60))
        else:
            disabled_cogs.append(togglethingy)
            write_server_config(ctx.guild.id, 'disabled_cogs', disabled_cogs)
            await ctx.reply(get_language_str(ctx.guild.id, 61))

    @disablecog_command.error
    async def disablecmd_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name='cleardata',
        description='Clears out a guild\'s data.\n'
                    '**VERY DANGEROUS, AS THIS WILL MAKE THE BOT LEAVE AND '
                    'CLEAR OUT EVERYTHING ASSOCIATED WITH THIS SERVER! USE AT YOUR OWN RISK.**',
        usage='',
        brief='Erases the guild\'s entire data (!!)'
    )
    @commands.has_guild_permissions(administrator=True)
    async def cleardata_command(self, ctx):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send("Woah there! Are you sure you know what you're doing?\n"
                       "**This will clear out all data associated to this server from the bot's data after 3 days**, "
                       "then make the bot itself leave! *This will also unmute all currently muted users.* "
                       "If you decide to invite the bot back, the data deletion will be cancelled and your data should "
                       "be left intact.\n**Are you sure you want to continue?** *(y/n)*")
        # I'd really prefer not to translate this.

        replymsg = await self.bot.wait_for('message', check=check)
        reply = replymsg.content.lower()
        if reply in ('y', 'yes', 'confirm'):
            pass
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):
            await ctx.send("Got it. *False alarm, everyone! Continue back to what you were doing. No data has been "
                           "queued for deletion.*")
            return
        else:
            await ctx.send("Uh, I'll take that as a no. *Action cancelled.*")
            return

        dt_obj = cal.parseDT(datetimeString='3 days')  # I feel like Todd Howard. It just works, but there's got to be
        now_dt = datetime.now()                        # a better way of doing this.
        list_now_dt = str(now_dt).split(":")
        list_dt_obj = str(dt_obj[0]).split(":")

        str_now_dt = f'{list_now_dt[0]}:{list_now_dt[1]}'
        str_dt_obj = f'{list_dt_obj[0]}:{list_dt_obj[1]}'

        # The unthinkable will be done.
        with open("data/data_clear.json", "r+", newline='\n', encoding='utf-8') as tempf:
            data_clear = json.load(tempf)
            guild = ctx.guild
            if str_dt_obj not in data_clear:
                data_clear[str_dt_obj] = []
            data_clear[str_dt_obj].append(str(guild.id))
            clear_index = len(data_clear[str_dt_obj]) - 1
            if str(guild.id) not in data_clear:
                data_clear[str(guild.id)] = []
            data_clear[str(guild.id)] = [str_dt_obj, clear_index]
            tempf.seek(0)
            json.dump(data_clear, tempf, indent=2)
            tempf.truncate()

        # Unmute all current mutes
        with open("data/unmutes.json", "r", encoding="utf-8", newline="\n") as unmutef:
            unmutes = json.load(unmutef)
            unmute_desc = ""
            if str(guild.id) in unmutes:
                # Guess what, we have mutes!.. god dammit.
                diction = {}
                for userID, data in unmutes[str(guild.id)].items():
                    user = guild.get_member(int(userID))
                    unmute_time = data[0]
                    unmute_index = data[2]
                    unmute_date_entry = unmutes[unmute_time][unmute_index]
                    unmute_role_id = unmute_date_entry[1]
                    unmute_role = discord.utils.get(guild.roles, id=int(unmute_role_id))
                    await user.remove_roles(unmute_role)
                    unmute_desc = unmute_desc + f'{user.name} (unmute time would be at {unmute_time})\n'
                    if diction.get(unmute_time):
                        # Already exists.
                        time_thing = diction[unmute_time]
                        time_thing.append(unmute_index)
                        diction[unmute_time] = time_thing
                    else:
                        # Doesn't exist.
                        diction[unmute_time] = [unmute_index]
                unmutes.pop(str(guild.id))
                for time, indexes in diction.items():
                    indexes.sort(reverse=True)
                    for index in indexes:
                        unmutes[time].pop(index)
                    if not unmutes[time]:
                        unmutes.pop(time)
                with open("data/unmutes.json", "w", encoding="utf-8", newline="\n") as writef:
                    json.dump(unmutes, writef, indent=2)

        embed = discord.Embed(
            title="Data deletion queued",
            description=f"Date until deletion: {str_dt_obj} *(now is {str_now_dt})*\n"
                        f"Server ID: {guild.id}",
            color=random.choice(color_list)
        )
        if unmute_desc:
            embed.add_field(
                name='Unmuted members',
                value=unmute_desc
            )
        embed.set_author(
            name=ctx.author.name,
            icon_url=ctx.author.avatar_url,
            url=f"https://discord.com/users/{ctx.author.id}/"
        )
        with open("data/quotes/goodbyes.json", encoding='utf-8', newline="\n") as goodbyes_json:
            goodbyes = json.load(goodbyes_json)
        await ctx.reply(random.choice(goodbyes).format(ctx), embed=embed)
        await ctx.guild.leave()

    @cleardata_command.error
    async def cleardata_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return

    @commands.command(
        name="changelang",
        description="Changes the guild's bot language, if it exists.\n"
                    "'default' is English.",
        aliases=["language", "changelanguage"],
        brief="Change the language of this bot"
    )
    @has_guild_permissions(manage_guild=True)
    async def banword_command(self, ctx, *, commandargs=None):
        # NOTICE: DO NOT TRANSLATE THIS COMMAND!
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author
        if not commandargs:
            await ctx.send("What would you like to change the language to?")
            msg = await self.bot.wait_for('message', check=check)
            commandargs = msg.content
        else:
            commandargs = commandargs.replace(' ', '')
        commandargs = commandargs.lower()

        if commandargs in get_all_languages():
            # language exists
            write_server_config(ctx.guild.id, 'language', commandargs)
            await ctx.reply(get_language_str(commandargs, 4).format(get_server_config(ctx.guild.id, 'prefix', str)))
        else:
            # me no habla whatever the hell kind of language they want to tell me
            await ctx.reply("Could not find that language, no changes made.")

    @tasks.loop(minutes=1)
    async def data_clearer(self):
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("data/data_clear.json", "r", encoding="utf-8", newline="\n") as file:
            data_clear = json.load(file)

        if dt_string in data_clear:
            guilds = []
            now_clears = data_clear.get(dt_string)
            for toClear in now_clears:
                guild_id = toClear
                try:
                    shutil.rmtree(f'data/servers/{guild_id}/')
                except OSError:
                    pass  # Directory already removed (???)
                guilds.append(guild_id)
                now_clears = [x for x in now_clears if x != toClear]
            # Stuff done, remove leftovers 2: electric boogaloo
            with open("data/data_clear.json", "r+", encoding='utf-8', newline="\n") as data_clear_json:
                data_clears = json.load(data_clear_json)
                data_clears.pop(dt_string)
                for toPop in guilds:
                    data_clears.pop(str(toPop))
                data_clear_json.seek(0)
                json.dump(data_clears, data_clear_json, indent=2)
                data_clear_json.truncate()


def setup(bot):
    bot.add_cog(Configuration(bot))
