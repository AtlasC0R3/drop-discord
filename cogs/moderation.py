import time
import json
import random
import os

import discord
from discord.ext import commands

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='purge',
        description='Deletes a certain amount of messages.',
        usage='5',
        brief='Deletes a set amount of messages'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_command(self, ctx, to_delete=5):
        if to_delete <= 0:
            await ctx.send("Invalid amount specified: you can't put a number under 1! "
                           "*Action cancelled.*")
            return

        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(f"[{ctx.author.name}], are you sure you want to delete [{to_delete}] messages?")
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()  # Set the confirmation
        if reply in ('y', 'yes', 'confirm'):
            await ctx.channel.purge(limit=to_delete + 3)
            temp_message = await ctx.send(f"[{ctx.author.name}], deleted [{to_delete}] messages.")
            time.sleep(5)
            await temp_message.delete()
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):  # idk why i decided to put flanksteak there
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what you want me to do. Action cancelled.")
            return

    @commands.command(
        name='rules',
        description='Prints a specific rule.',
        usage='3',
        aliases=['rule'],
        brief='Prints a server rule'
    )
    async def rules_command(self, ctx, rule: str):
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        try:
            open(rulefile, 'r', newline="\n", encoding="utf-8")
        except FileNotFoundError:
            await ctx.send("I have found no rules for this server.")
            return

        rules = json.load(open(rulefile, "r", encoding="utf-8", newline="\n"))

        rule_desc = rules.get(rule.lower())
        if rule_desc is None:
            await ctx.send(f"[{ctx.message.author.name}], you specified an invalid rule.")
            return

        embed = discord.Embed(
            title=f"Rule {rule}",
            description=f"{rule_desc}",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        await ctx.send(
            embed=embed,
            content=None
        )

    @rules_command.error
    async def rules_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rule':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule.")
                return

    @commands.command(
        name='set_rule',
        description='Sets a new rule. Can also edit an already existing rule',
        usage='5a\n(as part of a separate message) no nsfw!!!!1!',
        aliases=['addrule', 'newrule', 'editrule', 'edit_rule', 'setrule'],
        brief='Add a rule to the server.'
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def addrule_command(self, ctx, rulekey):
        rulepath = 'data/servers/' + str(ctx.guild.id) + '/'
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        if not os.path.exists(rulepath):
            os.makedirs(rulepath)
        if os.path.exists(rulefile):
            ruledata = json.load(open(rulefile, encoding="utf-8", newline="\n"))
        else:
            ruledata = {}

        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send("What shall be the rule description?")
        replymsg = await self.bot.wait_for('message', check=check)
        rulevalue = replymsg.content
        ruledata[rulekey.lower()] = rulevalue

        json.dump(ruledata, open(rulefile, 'w+', newline='\n', encoding="utf-8"), indent=2)

        await ctx.send("Success, rule has been added.")

    @addrule_command.error
    async def addrule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule name.")
                return

    @commands.command(
        name='remove_rule',
        description='Remove a rule',
        usage='5a',
        aliases=['rmrule', 'delrule', 'deleterule', 'delete_rule', 'poprule'],
        brief='Remove a rule for the server'
    )
    async def poprule_command(self, ctx, rulekey):
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        if not os.path.exists(rulefile):
            await ctx.send("There are no rules for this server.")
            return

        with open(rulefile, 'r+', newline="\n", encoding="utf-8") as rulefileobject:
            ruledata = json.load(rulefileobject)
            try:
                ruledata.pop(rulekey.lower())
            except KeyError:
                await ctx.send("The specified rule does not exist.")
                rulepopped = False
            else:
                rulepopped = True
            if ruledata == {}:
                rulefileobject.close()
                os.remove(rulefile)
            else:
                json.dump(ruledata, open(rulefile, 'w+', newline='\n', encoding='utf-8'), indent=2)
                rulefileobject.close()

        if rulepopped:
            await ctx.send("Success, rule has been deleted.")

    @poprule_command.error
    async def poprule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule name.")
                return

    @commands.command(
        name='kick',
        description='Kicks a specified user. Not sure why you\'d want to use the bot for this, but okay.',
        usage='<@offender> reason (optional)',
        brief='Kicks a user'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def kick_command(self, ctx, user: discord.Member, *, reason=None):
        if user.id == self.bot.user.id:
            await ctx.send("Really..? After all my efforts, this is how I get treated?")
            return
        if user == ctx.author:
            await ctx.send("You hate yourself *that* much?")
            return
        if user.guild_permissions.manage_messages:
            await ctx.send("The specified user has the \"Manage Messages\" permission "
                           "(or higher) inside the guild/server.")
            return
        if reason is None:
            reason = "No reason specified."
        await user.kick(reason=f'{reason}\n(Kicked by {ctx.author.name})')
        embed = discord.Embed(
            title="User kicked",
            description=f"User: **{user}**\n"
                        f"Reason: **{reason}**\n"
                        f"Kicked by: **{ctx.author}**",
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.send(embed=embed)

    @kick_command.error
    async def kick_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f'{error} *(Action cancelled.)*')
            return
        elif isinstance(error, discord.Forbidden):
            await ctx.send(f'Seems like I am missing permissions to do so.')
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("You did not specify a user to kick. *Action cancelled.*")
                return
            else:
                await ctx.send(f"Required argument {error.param.name} is missing.")

    @commands.command(
        name='ban',
        description='Bans a specified user. Not sure why you wouldn\'t want to do it yourself, but okay.',
        usage='<@offender> reason (optional)',
        brief='Bans a user'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def ban_command(self, ctx, user: discord.Member, *, reason=None):
        if user.id == self.bot.user.id:
            await ctx.send("Really..? After all my efforts, this is how I get treated?")
            return
        if user == ctx.author:
            await ctx.send("You hate yourself *that* much?")
            return
        if user.guild_permissions.manage_messages:
            await ctx.send("The specified user has the \"Manage Messages\" permission "
                           "(or higher) inside the guild/server.")
            return
        if reason is None:
            reason = "No reason specified."
        await user.ban(reason=f'{reason}\n(Banned by {ctx.author.name})')
        embed = discord.Embed(
            title="User banned",
            description=f"User: **{user}**\n"
                        f"Reason: **{reason}**\n"
                        f"Banned by: **{ctx.author}**",
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.send(embed=embed)

    @ban_command.error
    async def ban_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.send(f'{error} *(Action cancelled.)*')
            return
        elif isinstance(error, discord.Forbidden):
            await ctx.send(f'Seems like I am missing permissions to do so.')
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("You did not specify a user to ban. *Action cancelled.*")
                return
            else:
                await ctx.send(f"Required argument {error.param.name} is missing.")

    @commands.command(
        name='unban',
        description='Unbans a specified user. Again, I don\'t know why you wouldn\' want to do it yourself.',
        usage='<@offender>',
        brief='Unbans a user'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def unban_command(self, ctx, *, user):
        banlist = await ctx.guild.bans()
        if user.isdigit():
            # The user has been specified using an ID.
            for entry in banlist:
                if entry.user.id == int(user):
                    # We have found the correct user
                    user = entry.user
        elif '#' in user:
            # The user also comes with a discriminator.
            userfull = user.split('#')
            if len(userfull) != 2:
                await ctx.send("Whoops, there seems to be more than one discriminator in that user. "
                               "This is making my task of finding the user you are looking for impossible. "
                               "*Action cancelled.*")
                return
            elif type(userfull) is not list:
                await ctx.send("Whoops, I seem to have screwed something up (or Python is becoming unreliable), "
                               "so now I can't find the user you are looking for. I'll take the blame. "
                               "*Action cancelled.*")
                return
            for entry in banlist:
                if (userfull[0], userfull[1]) == (entry.user.name, entry.user.discriminator):
                    # We have found the correct user
                    user = entry.user
        else:
            # That must be just the user's name.
            for entry in banlist:
                if user == entry.user.name:
                    # We have found the correct user
                    user = entry.user

        if user.id == self.bot.user.id:
            await ctx.send("Hey, I'm not banned, I can still talk here.")
            return
        if user == ctx.author:
            await ctx.send("Yeah, you're not banned.")
            return

        await ctx.guild.unban(user)
        embed = discord.Embed(
            title="User unbanned",
            description=f"User: **{user}**\n"
                        f"Unbanned by: **{ctx.author}**",
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.send(embed=embed)

    @unban_command.error
    async def unban_handler(self, ctx, error):
        if isinstance(error, commands.UserNotFound):
            await ctx.send(f'{error} *(Action cancelled.)*')
            return
        elif isinstance(error, discord.Forbidden):
            await ctx.send(f'Seems like I am missing permissions to do so.')
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.send("You did not specify a user to unban. *Action cancelled.*")
                return
            else:
                await ctx.send(f"Required argument {error.param.name} is missing.")

    @commands.command(
        name='storepins',
        description='Stores all of the pinned messages in a certain channel.',
        usage='storepins <#channel to store pins in>',
        brief='Store all of the pins in a channel',
        aliases=['savepins', 'pincenter']
    )
    async def storepins_command(self, ctx, channel):
        pins = reversed(await ctx.channel.pins())
        for pin in pins:
            replace = {' ': '',
                       '<': '',
                       '#': '',
                       '>': ''}
            for key, value in replace.items():
                channel = channel.replace(key, value)
            if channel.isdigit():
                channelsendin = ctx.guild.get_channel(int(channel))
                if channel is None:
                    await ctx.send("Uh oh, I could not get the channel you meant. Please try again. "
                                   "If it still fails, please try directly inserting the channel's ID. "
                                   "*Action cancelled.*")
                    return
            else:
                channelsendin = discord.utils.get(self.bot.get_all_channels(), guild=ctx.guild, name=channel)
                if channel is None:
                    await ctx.send("Whoops, I couldn't find the channel you meant. "
                                   "Please try again by directly mentioning the channel you mean. *Action cancelled.*")
                    return

            if pin.attachments:
                embed = discord.Embed(
                    title=f"Pinned message in #{pin.channel.name}",
                    description=f"{pin.content}\n{pin.attachments[0].url}",
                    color=random.choice(color_list)
                )
            else:
                embed = discord.Embed(
                    title=f"Pinned message in #{pin.channel.name}",
                    description=f"{pin.content}",
                    color=random.choice(color_list)
                )
            embed.set_author(
                name=pin.author.name,
                icon_url=pin.author.avatar_url,
                url=f"https://discord.com/users/{pin.author.id}/"
            )
            embed.add_field(
                name='Message link',
                value=f'https://discordapp.com/channels/{pin.guild.id}/{pin.channel.id}/{pin.id}'
            )
            await channelsendin.send(embed=embed)
            time.sleep(5)
        await ctx.send('Done storing pins.')

    @storepins_command.error
    async def storepins_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a channel.")
                return


def setup(bot):
    bot.add_cog(Moderation(bot))
