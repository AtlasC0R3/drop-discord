import random
import discord
from discord.ext import commands, tasks

from data.extdata import get_server_config, get_language_str
from drop.mute import *
from drop.errors import PastTimeError, PresentTimeError, InvalidTimeParsed

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Mute(commands.Cog):
    """
    All of the commands for muting someone.
    """

    def __init__(self, bot):
        self.bot = bot
        self.unmute_task.start()

    @commands.command(
        name='mute',
        description='Removes a user\'s ability to talk (if the muted role is configured to do so).\n'
                    'Also works with multiple users.',
        usage='<@offender 1> <@offender 2> 1h30',
        brief='Mutes a user'
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def mute_command(self, ctx, users: commands.Greedy[discord.Member], *, timestamp):
        if get_server_config(ctx.guild.id, 'mute_role', int) == 0:
            await ctx.reply(get_language_str(ctx.guild.id, 85))
            return
        role = ctx.guild.get_role(get_server_config(ctx.guild.id, 'mute_role', int))
        if not users:
            await ctx.reply(get_language_str(ctx.guild.id, 90).format(ctx.author.name, "No users specified."))
            return
        for user in users:
            if role in user.roles:
                await ctx.reply(get_language_str(ctx.guild.id, 86).format(ctx.author.name))
                return
            else:
                pass

            await user.add_roles(role)

            try:
                str_dt_obj = add_mutes(ctx.guild.id, role.id, user.id, ctx.author.id, timestamp)
            except InvalidTimeParsed:
                await ctx.send(get_language_str(ctx.guild.id, 87))
                return
            except PastTimeError:
                await ctx.send(get_language_str(ctx.guild.id, 88))
                return
            except PresentTimeError:
                await ctx.send(get_language_str(ctx.guild.id, 89))
                return

            embed = discord.Embed(
                title="User muted",
                description=f"User: **{user}**\n"
                            f"Time until the user will be unmuted: **{str_dt_obj}**\n"
                            f"Muted by: **{ctx.author}**",
                color=random.choice(color_list)
            )
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )

            await ctx.reply(embed=embed)

    @mute_command.error
    async def mute_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'timestamp':
                await ctx.reply(get_language_str(ctx.guild.id, 91).format(ctx.author.name, str(error)))
                return
            return

    @commands.command(
        name='mute_status',
        description='Checks if the user is muted, and for how long/by who he has been muted.',
        usage='<@potentially muted person>',
        brief='Checks a user\'s mute status',
        aliases=["checkmute", "check_mute", "mutestatus"]
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def mutestatus_command(self, ctx, users: commands.Greedy[discord.Member]):
        if not users:
            await ctx.reply(get_language_str(ctx.guild.id, 126).format(ctx.author.name))
        for user in users:
            try:
                user_mute = get_mute_status(ctx.guild.id, user.id)
            except NoMutesForGuild:
                await ctx.reply(get_language_str(ctx.guild.id, 92))
                return
            except NoMutesForUser:
                await ctx.reply(get_language_str(ctx.guild.id, 93).format(user.name))
                return
            # user has been muted.
            mute_time = user_mute.get("unmute_time")
            muter_id = user_mute.get("mute_author_id")
            muter = ctx.guild.get_member(muter_id)
            # mute_index = user_mute.get("mute_index")
            # mute_data = user_mute.get("mute_data")
            # mute_role_id = user_mute.get("mute_role_id")
            # mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)

            embed = discord.Embed(
                title=f"{user}'s mute status",
                description=f"Time until the user will be unmuted: **{mute_time}**\n"
                            f"Muted by: **{muter}**",
                color=random.choice(color_list)
            )
            embed.set_thumbnail(url=user.avatar_url)
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )

            await ctx.reply(embed=embed)

    @mutestatus_command.error
    async def mutestatus_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(f'[{ctx.author.name}], you did not specify a user. '
                                f'*({error} Action cancelled)*')
                return

    @commands.command(
        name='unmute',
        description='Unmutes a person who is currently muted.',
        usage='<@muted person>',
        brief='Unmutes a person'
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def unmute_command(self, ctx, users: commands.Greedy[discord.Member]):
        for user in users:
            mute_role_id = unmute_user(ctx.guild.id, user.id)
            # seems messy but unmute_user() not only returns the mute role's ID but also deletes all mute data for
            # specified user
            mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)
            await user.remove_roles(mute_role)

        await ctx.reply(get_language_str(ctx.guild.id, 95))
        # Oh, wow. After moving this command over to the Python module it looks really neat,
        # until you were to check what unmute_user() does.

    @unmute_command.error
    async def unmute_handler(self, ctx, error):
        if isinstance(error, commands.errors.MissingPermissions):
            await ctx.reply(get_language_str(ctx.guild.id, 28).format(ctx.author.name, error))
            return
        if isinstance(error, commands.errors.MissingRequiredArgument):
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 96).format(ctx.author.name, error))
                return

    @tasks.loop(minutes=1)
    async def unmute_task(self):
        unmutes = check_mutes()
        if unmutes:
            for toUnmute in unmutes:
                guild_id = toUnmute["guild_id"]
                guild = self.bot.get_guild(guild_id)
                role_id = toUnmute["role_id"]
                role = discord.utils.get(guild.roles, id=role_id)
                user_id = toUnmute["user_id"]
                user_member = guild.get_member(user_id)  # holy s*** i need to learn intents.
                await user_member.remove_roles(role)
        # So now we have taken care of the current mutes. check_mutes() takes care of pretty much everything, too.
        # The only thing this task-loop does is just tell check_mutes to get all mutes (and clear them), and then
        # uses Discord.py to get a member from a guild, and remove the muted role as configured.


def setup(bot):
    bot.add_cog(Mute(bot))
