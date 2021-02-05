import json
import ast
import random

import discord
from discord.ext import commands
from data.extdata import get_config_parameter, get_steam_recently_played


class Owner(commands.Cog):
    """
    Commands that are meant to only be used by the bot owner, as configured in config.json.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='activity',
        description='Changes the bot\'s activity. A list, a string or an index can be inserted.',
        brief='Changes the bot\'s activity'
    )
    @commands.is_owner()
    async def activity_command(self, ctx, *, activity=None):
        with open("data/activities.json", encoding='utf-8', newline="\n") as f:
            activities = json.load(f)
            activitytype = None
            activityname = None
        if activity:
            if activity.startswith('[') or activity.isdigit():
                activityentry = ast.literal_eval(activity)
                if type(activityentry) is int:
                    try:
                        activity = activities[activityentry]
                    except IndexError:
                        await ctx.send("Wrong activity! **>:(**")
                        return
                    activitytype = activity[0]
                    activityname = activity[1]
                    await ctx.send(content=f'{activitytype.title()} {activityname}, is this correct?')

                    def check(ms):
                        return ms.channel == ctx.message.channel and ms.author == ctx.message.author
                    replymsg = await self.bot.wait_for('message', check=check)
                    reply = replymsg.content.lower()

                    if reply in ('y', 'yes', 'confirm'):
                        pass
                    elif reply in ('n', 'no', 'cancel'):
                        await ctx.send("Got it.")
                        return
                elif type(activityentry) is list:
                    try:
                        activitytype = activityentry[0]
                        activityname = activityentry[1]
                        await self.bot.change_presence(
                            activity=discord.Activity(type=discord.ActivityType[activitytype], name=activityname))
                    except (KeyError, IndexError):
                        await ctx.send("Invalid list! Here's an example of how an activity list should be:\n"
                                       f"```{random.choice(activities)}```")
                        return
            else:
                activitylist = activity.split(' ')
                if activitylist[0] in [x.name for x in discord.ActivityType]:
                    activitytype = activitylist[0]
                    activityname = " ".join(activitylist[1:])
                else:
                    activitytype = 'playing'
                    activityname = activity
        else:
            if get_config_parameter('useSteamRecentlyPlayed', int) != 0:
                for game in get_steam_recently_played():
                    activities.append(['playing', game])
            activity = random.choice(activities)
            activitytype = activity[0]
            activityname = activity[1]
        await self.bot.change_presence(
            activity=discord.Activity(type=discord.ActivityType[activitytype], name=activityname))
        await ctx.reply(content=f'{activitytype.title()} {activityname}')


def setup(bot):
    bot.add_cog(Owner(bot))
