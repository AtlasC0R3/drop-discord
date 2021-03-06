import time
import random

import discord
from discord.ext import commands
from data.extdata import get_language_str

from drop.moderation import *
from drop.errors import *

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Moderation(commands.Cog):
    """
    Commands that (hopefully) may help you moderate the server
    """

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
            await ctx.reply(get_language_str(ctx.guild.id, 62))
            return

        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(get_language_str(ctx.guild.id, 63).format(ctx.author.name, str(to_delete)))
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()  # Set the confirmation
        if reply in ('y', 'yes', 'confirm'):
            await ctx.channel.purge(limit=to_delete + 3)
            temp_message = await ctx.send(get_language_str(ctx.guild.id, 64).format(ctx.author.name, str(to_delete)))
            time.sleep(5)
            await temp_message.delete()
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):  # idk why i decided to put flanksteak there
            await ctx.send(26)
            return
        else:
            await ctx.send(27)
            return

    @commands.command(
        name='rules',
        description='Prints a specific rule.',
        usage='3',
        aliases=['rule'],
        brief='Prints a server rule'
    )
    async def rules_command(self, ctx, rule: str):
        try:
            rule_desc = get_rules(ctx.guild.id).get(rule.lower())
        except NoRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 65))
            return
        except BrokenRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 123))
            return
        if not rule_desc:
            await ctx.reply(get_language_str(ctx.guild.id, 66).format(ctx.message.author.name))
            return

        embed = discord.Embed(
            title=f"Rule {rule.lower()}",
            description=f"{rule_desc}",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        await ctx.reply(
            embed=embed,
            content=None
        )

    @rules_command.error
    async def rules_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rule':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
                return

    @commands.command(
        name='set_rule',
        description='Sets a new rule. Can also edit an already existing rule',
        usage='5a\n(as part of a separate message) no nsfw!!!!1!',
        aliases=['addrule', 'newrule', 'editrule', 'edit_rule', 'setrule'],
        brief='Set a rule to the server.'
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def addrule_command(self, ctx, rulekey):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(get_language_str(ctx.guild.id, 68))
        replymsg = await self.bot.wait_for('message', check=check)
        rulevalue = replymsg.content
        try:
            set_rule(ctx.guild.id, rulekey, rulevalue)
        except BrokenRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 123))
            return

        await ctx.reply(get_language_str(ctx.guild.id, 69))
        # hghghgh funny number please help its 9:40 pm im fucking tired
        # hey past self, i just want you to know you're a champ for going through this hassle. you're the best. -atlas

    @addrule_command.error
    async def addrule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
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
            await ctx.reply(get_language_str(ctx.guild.id, 70))
            return

        try:
            pop_rule(ctx.guild.id, rulekey)
        except KeyError:
            await ctx.reply(get_language_str(ctx.guild.id, 71))
            return

        await ctx.reply(get_language_str(ctx.guild.id, 72))

    @poprule_command.error
    async def poprule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
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
            await ctx.reply(get_language_str(ctx.guild.id, 73))
            # totally not inspired by carlbot
            return
        if user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 74))
            return
        if user.guild_permissions.manage_messages:
            await ctx.reply(get_language_str(ctx.guild.id, 75))
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
        await ctx.reply(embed=embed)

    @kick_command.error
    async def kick_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.reply(f'{error} *(Action cancelled.)*')
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 76))
                return

    @commands.command(
        name='ban',
        description='Bans a specified user. Not sure why you wouldn\'t want to do it yourself, but okay.',
        usage='<@offender> reason (optional)',
        brief='Bans a user'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def ban_command(self, ctx, user: discord.Member, *, reason=None):
        if user.id == self.bot.user.id:
            await ctx.reply(get_language_str(ctx.guild.id, 73))
            # again totally not inspired by carlbot
            return
        if user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 74))
            return
        if user.guild_permissions.manage_messages:
            await ctx.reply(get_language_str(ctx.guild.id, 75))
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
        await ctx.reply(embed=embed)

    @ban_command.error
    async def ban_handler(self, ctx, error):
        if isinstance(error, commands.MemberNotFound):
            await ctx.reply(f'{error} *(Action cancelled.)*')
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 77))
                return

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
                await ctx.reply(get_language_str(ctx.guild.id, 78))
                return
            elif type(userfull) is not list:
                await ctx.reply(get_language_str(ctx.guild.id, 79))
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
            await ctx.reply(get_language_str(ctx.guild.id, 80))
            return
        if user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 81))
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
        await ctx.reply(embed=embed)

    @unban_command.error
    async def unban_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 82))
                return

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
                    await ctx.reply(get_language_str(ctx.guild.id, 83))
                    return
            else:
                channelsendin = discord.utils.get(self.bot.get_all_channels(), guild=ctx.guild, name=channel)
                if channel is None:
                    await ctx.reply(get_language_str(ctx.guild.id, 36))
                    return

            embed = discord.Embed(
                title=f"Pinned message in #{pin.channel.name}",
                description=f"{pin.content}",
                color=random.choice(color_list)
            )
            if pin.attachments:
                attachments = ""
                for attachment in pin.attachments:
                    attachments = attachments + attachment.url + '\n'
                embed.add_field(
                    name='Attachments',
                    value=attachments
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
        await ctx.reply('Done storing pins.')

    @storepins_command.error
    async def storepins_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.reply(get_language_str(ctx.guild.id, 84).format(ctx.message.author.name))
                return


def setup(bot):
    bot.add_cog(Moderation(bot))
