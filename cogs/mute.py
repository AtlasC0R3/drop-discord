import json
import random
import discord
from discord.ext import commands, tasks
from datetime import datetime
import parsedatetime

from data.extdata import get_server_config, get_language_str

cal = parsedatetime.Calendar()

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
        description='Removes a user\'s ability to talk (if the muted role is configured to do so).',
        usage='<@offender> 1h30',
        brief='Mutes a user'
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def mute_command(self, ctx, user: discord.Member, *, timestamp):
        if get_server_config(ctx.guild.id, 'mute_role', int) == 0:
            await ctx.reply(get_language_str(ctx.guild.id, 85))
            return
        role = ctx.guild.get_role(get_server_config(ctx.guild.id, 'mute_role', int))
        if role in user.roles:
            await ctx.reply(get_language_str(ctx.guild.id, 86).format(ctx.author.name))
            return
        else:
            pass

        dt_obj = cal.parseDT(datetimeString=timestamp)
        now_dt = datetime.now()
        list_dt_obj = str(dt_obj[0]).split(":")
        list_now_dt = str(now_dt).split(":")

        str_now_dt = f'{list_now_dt[0]}:{list_now_dt[1]}'
        str_dt_obj = f'{list_dt_obj[0]}:{list_dt_obj[1]}'

        if dt_obj[1] == 0:
            await ctx.send(get_language_str(ctx.guild.id, 87))
            return
        elif dt_obj[0] <= now_dt:
            await ctx.send(get_language_str(ctx.guild.id, 88))
            return
        elif dt_obj[0] == now_dt or str_dt_obj == str_now_dt:
            await ctx.send(get_language_str(ctx.guild.id, 89))
            return

        await user.add_roles(role)

        with open("data/unmutes.json", "r+", newline='\n', encoding='utf-8') as tempf:
            penalties = json.load(tempf)
            guild = ctx.guild
            mute_data = ([user.id, role.id, guild.id])
            if str_dt_obj not in penalties:
                penalties[str_dt_obj] = []
            penalties[str_dt_obj].append(mute_data)
            mute_index = len(penalties[str_dt_obj]) - 1
            if str(guild.id) not in penalties:
                penalties[str(guild.id)] = {}
            if str(user.id) in penalties[str(guild.id)]:
                penalties[str(guild.id)].pop(str(user.id))
            if not str(user.id) in penalties[str(guild.id)]:
                penalties[str(guild.id)][str(user.id)] = []
            penalties[str(guild.id)][str(user.id)] = [str_dt_obj, ctx.author.id, mute_index]
            tempf.seek(0)
            json.dump(penalties, tempf, indent=2)
            tempf.truncate()

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
            if error.param.name == 'user':
                await ctx.reply(get_language_str(ctx.guild.id, 90).format(ctx.author.name, str(error)))
                return
            if error.param.name == 'timestamp':
                await ctx.reply(get_language_str(ctx.guild.id, 91).format(ctx.author.name, str(error)))
                return
            return

    @commands.command(
        name='mute_status',
        description='Checks if the user is muted, and for how long/by who he has been muted.',
        usage='<@potentially muted person>',
        brief='Checks a user\'s mute status'
    )
    @commands.has_guild_permissions(manage_roles=True)
    async def mutestatus_command(self, ctx, user: discord.Member):
        guild_id = ctx.guild.id
        with open("data/unmutes.json", "r", newline='\n', encoding='utf-8') as tempf:
            mutes = json.load(tempf)
            guild_mutes = mutes.get(str(guild_id))
            if guild_mutes is None:
                await ctx.reply(get_language_str(ctx.guild.id, 92))
                return
            user_mutes = guild_mutes.get(str(user.id))
            if not user_mutes:
                await ctx.reply(get_language_str(ctx.guild.id, 93).format(user))
                return
            # user has been muted.
            mute_time = user_mutes[0]
            muter_id = user_mutes[1]
            muter = ctx.guild.get_member(muter_id)
            # mute_index = user_mutes[2]
            # mute_data = mutes.get(mute_time)[mute_index]
            # mute_role_id = mute_data[2]
            # mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)

        embed = discord.Embed(
            title=f"{user}'s mute status",
            description=f"Time until the user will be unmuted: {mute_time}\n"
                        f"Muted by: {muter}\n",
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
    async def unmute_command(self, ctx, user: discord.Member):
        guild_id = ctx.guild.id
        with open("data/unmutes.json", "r+", newline='\n', encoding='utf-8') as tempf:
            mutes = json.load(tempf)
            guild_mutes = mutes.get(str(guild_id))
            if guild_mutes is None:
                await ctx.reply(get_language_str(ctx.guild.id, 94))
                return
            user_mutes = guild_mutes.get(str(user.id))
            if not user_mutes:
                await ctx.reply(get_language_str(ctx.guild.id, 93).format(user))
                return
            # user has been muted.
            mute_time = user_mutes[0]
            mute_index = user_mutes[2]
            mute_data = mutes.get(mute_time)[mute_index]
            mute_role_id = mute_data[1]
            mute_role = discord.utils.get(ctx.guild.roles, id=mute_role_id)
            await user.remove_roles(mute_role)
            mutes.get(mute_time).pop(mute_index)
            if not mutes.get(mute_time):
                mutes.pop(mute_time)
            guild_mutes.pop(str(user.id))
            if not guild_mutes:
                mutes.pop(str(guild_id))
            tempf.seek(0)
            json.dump(mutes, tempf, indent=2)
            tempf.truncate()

        await ctx.reply(get_language_str(ctx.guild.id, 95))

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
        dt_string = datetime.now().strftime("%Y-%m-%d %H:%M")
        with open("data/unmutes.json", "r", encoding="utf-8", newline="\n") as file:
            unmutes = json.load(file)
        if dt_string in unmutes:
            guilds = []
            users = []
            for toUnmute in unmutes.get(dt_string):
                guild_id = toUnmute[2]
                guild = self.bot.get_guild(guild_id)
                role_id = toUnmute[1]
                role = discord.utils.get(guild.roles, id=role_id)
                user_id = toUnmute[0]
                user_member = guild.get_member(user_id)  # holy s*** i need to learn intents.
                await user_member.remove_roles(role)
                toUnmute.pop()
                guilds.append(guild_id)
                users.append(user_id)
            # Stuff done, remove leftovers
            with open("data/unmutes.json", "r+", encoding='utf-8', newline="\n") as unmuteFile:
                unmutes = json.load(unmuteFile)
                unmutes.pop(dt_string)
                for toUnmute in users:
                    for y in guilds:
                        try:
                            unmutes[str(y)].pop(str(toUnmute))
                        except KeyError:
                            pass  # Wrong guild/user combination.
                        if not unmutes.get(str(y)):
                            unmutes.pop(str(y))
                unmuteFile.seek(0)
                json.dump(unmutes, unmuteFile, indent=2)
                unmuteFile.truncate()


def setup(bot):
    bot.add_cog(Mute(bot))
