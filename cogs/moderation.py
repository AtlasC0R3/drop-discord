import asyncio
import random

import discord
import drop.errors
from discord.ext import commands, tasks
from data.extdata import get_language_str, wait_for_user, get_file_type

from drop.tempban import *
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
        self.unban_task.start()

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

        do_purge = True
        if to_delete >= 10:
            msg = await ctx.send(get_language_str(ctx.guild.id, 63).format(ctx.author.name, str(to_delete)))
            do_purge = await wait_for_user(ctx, self.bot, msg)
            await msg.delete()
            await ctx.message.delete()
        if do_purge:
            try:
                await ctx.channel.purge(limit=to_delete)
            except discord.NotFound:
                pass
            temp_message = await ctx.send(get_language_str(ctx.guild.id, 64).format(ctx.author.name, str(to_delete)))
            await asyncio.sleep(5)
            await temp_message.delete()
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
                if (userfull[0].lower(), userfull[1]) == (entry.user.name.lower(), entry.user.discriminator):
                    # We have found the correct user
                    user = entry.user
        else:
            # That must be just the user's name.
            for entry in banlist:
                if user.lower() == entry.user.name.lower():
                    # We have found the correct user
                    user = entry.user

        if type(user) is str:
            await ctx.reply(get_language_str(ctx.guild.id, 82))
            return
        elif user.id == self.bot.user.id:
            await ctx.reply(get_language_str(ctx.guild.id, 80))
            return
        elif user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 81))
            return

        await ctx.guild.unban(user, reason=f"Manually unbanned by {ctx.author}")
        try:
            temp_ban = get_ban_status(ctx.guild.id, user.id)
        except NoTempBansForGuild:
            pass
        else:
            if temp_ban:
                # user is also temp-banned
                unban_user(ctx.guild.id, user.id)

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
    @commands.has_permissions(manage_messages=True)
    async def storepins_command(self, ctx, channel: discord.TextChannel):
        pins = await ctx.channel.pins()
        if not pins:
            await ctx.reply(get_language_str(ctx.guild.id, 135))
            return
        msg = await ctx.send(get_language_str(ctx.guild.id, 136))
        delete_pins = await wait_for_user(ctx, self.bot, msg, False)
        await msg.delete()

        do_sleep = False
        pins = reversed(pins)
        for pin in pins:
            if do_sleep:
                await asyncio.sleep(5)
            embed = discord.Embed(
                title=f"Pinned message in #{pin.channel.name}",
                description=pin.content,
                color=random.choice(color_list),
                url=pin.jump_url,
                timestamp=pin.created_at
            )
            msg_content = ""
            if pin.attachments:
                file_type = get_file_type(pin.attachments[0])
                if file_type == 1:
                    embed.set_image(url=pin.attachments[0].url)
                elif file_type == 2:
                    await channel.send(f'{pin.attachments[0].url} '
                                       f'**(putting this attachment link here so that the video can load, '
                                       f'since Discord currently does not allow videos inside bot embeds)**')
                if len(pin.attachments) > 1 or file_type != 1:
                    attachments = ""
                    for attachment in pin.attachments:
                        # attachments += attachment.url + '\n'
                        file_type = get_file_type(attachment)
                        attachments += f"[{attachment.filename} ({attachment.content_type})]" \
                                       f"({attachment.url})\n"
                    if file_type == 2:
                        attachments += "**The attached video has been sent as a separate message!**"
                    embed.add_field(
                        name='Attachments',
                        value=attachments
                    )
            embed.set_author(
                name=pin.author.name,
                icon_url=pin.author.avatar_url,
                url=f"https://discord.com/users/{pin.author.id}/"
            )
            await channel.send(content=msg_content, embed=embed)
            if delete_pins:
                await pin.delete()
            do_sleep = True
        await channel.send("`--- end of pins ---`")
        await ctx.reply('Done storing pins.')

    @storepins_command.error
    async def storepins_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'channel':
                await ctx.reply(get_language_str(ctx.guild.id, 84).format(ctx.message.author.name))
                return

    @commands.command(
        name='tempban',
        description='This will ban someone, then unban them after a specified time.',
        usage='<@offender 1> <@offender 2> 1h30',
        brief='Temporarily bans a user'
    )
    @commands.has_guild_permissions(ban_members=True)
    async def tempban_command(self, ctx, users: commands.Greedy[discord.Member], *, timestamp):
        if not users:
            await ctx.reply(get_language_str(ctx.guild.id, 90).format(ctx.author.name, "No users specified."))
            return
        for user in users:
            str_dt_obj = add_bans(ctx.guild.id, user.id, ctx.author.id, timestamp)
            await user.ban(reason=f"Banned by {ctx.author.name}, will be unbanned at: {str_dt_obj}")
            embed = discord.Embed(
                title="User temp-banned",
                description=f"User: **{user}**\n"
                            f"Time until the user will be unbanned: **{str_dt_obj}**\n"
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

    @tempban_command.error
    async def tempban_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'timestamp':
                await ctx.reply(get_language_str(ctx.guild.id, 91).format(ctx.author.name, str(error)))
                return
            return

    @commands.command(
        name='ban_status',
        description='Checks if the user is temp-banned, and for how long/by who they have been temp-banned.',
        usage='Offender#0123 (can also just be Offender, or their user ID)',
        brief='Checks a user\'s ban status',
        aliases=["checktempban", "check_tempban", "tempbanstatus", "banstatus"]
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def temp_ban_status_command(self, ctx, *, user: str):
        ban_list = await ctx.guild.bans()
        if user.isdigit():
            # The user has been specified using an ID.
            for entry in ban_list:
                if entry.user.id == int(user):
                    # We have found the correct user
                    user = entry.user
        elif '#' in user:
            # The user also comes with a discriminator.
            user_full = user.split('#')
            if len(user_full) != 2:
                await ctx.reply(get_language_str(ctx.guild.id, 78))
                return
            elif type(user_full) is not list:
                await ctx.reply(get_language_str(ctx.guild.id, 79))
                return
            for entry in ban_list:
                if (user_full[0], user_full[1]) == (entry.user.name, entry.user.discriminator):
                    # We have found the correct user
                    user = entry.user
        else:
            # That must be just the user's name.
            for entry in ban_list:
                if user.lower() == entry.user.name.lower():
                    # We have found the correct user
                    user = entry.user
        if type(user) is str:
            await ctx.send(get_language_str(ctx.guild.id, 82))
            return
        if user.id == self.bot.user.id:
            await ctx.reply(get_language_str(ctx.guild.id, 80))
            return
        if user == ctx.author:
            await ctx.reply(get_language_str(ctx.guild.id, 81))
            return
        try:
            temp_ban_data = get_ban_status(ctx.guild.id, user.id)
        except NoTempBansForGuild:
            await ctx.send(get_language_str(ctx.guild.id, 130))
            return
        if not temp_ban_data:
            await ctx.reply(get_language_str(ctx.guild.id, 131))
            return
        unban_time = temp_ban_data["unban_time"]
        ban_author_id = temp_ban_data["ban_author_id"]
        if ban_author_id == ctx.author.id:
            ban_author_name = ctx.author.name
        else:
            ban_author = ctx.guild.get_member(ban_author_id)
            if ban_author:
                ban_author_name = ban_author.name
            else:
                ban_author_name = "Someone who probably left"
        embed = discord.Embed(
            title=f"{user}'s temp-ban status",
            description=f"Time until the user will be unbanned: **{unban_time}**\n"
                        f"Temp-banned by: **{ban_author_name}**",
            color=random.choice(color_list)
        )
        embed.set_thumbnail(url=user.avatar_url)
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        await ctx.reply(embed=embed)

    @temp_ban_status_command.error
    async def temp_ban_status_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(f'[{ctx.author.name}], you did not specify a user. '
                                f'*({error} Action cancelled)*')
                return

    @tasks.loop(minutes=1)
    async def unban_task(self):
        unbans = check_bans()
        if unbans:
            for toUnban in unbans:
                guild_id = toUnban["guild_id"]
                guild = self.bot.get_guild(guild_id)
                user_id = toUnban["user_id"]
                ban_list = await guild.bans()
                for entry in ban_list:
                    if entry.user.id == int(user_id):
                        # We have found the correct user
                        await guild.unban(entry.user, reason="Their temp-ban period is over.")

    @commands.Cog.listener()
    async def on_member_unban(self, guild, user):
        # try:
        #     temp_ban = get_ban_status(guild.id, user.id)
        # except NoTempBansForGuild:
        #     pass
        # else:
        #     if temp_ban:
        #         # user is also temp-banned
        try:
            unban_user(guild.id, user.id)
        except drop.errors.NoTempBansForGuild:
            # Whoops, user wasn't tempbanned.
            pass


def setup(bot):
    bot.add_cog(Moderation(bot))
