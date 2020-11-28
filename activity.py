import discord
import json
from discord.ext import commands

bot = commands.Bot(
    command_prefix='+',
    description='Unavailable: Please don\'t try again later.',
    owner_id=333027024576970755,
    case_insensitive=True
)


@bot.event
async def on_ready():
    with open("data/activities.json", encoding='utf-8', newline="\n") as f:
        dictionary = json.load(f)
    activitynumber = input('give activity id:\n')
    activity = list(dictionary.values())[int(activitynumber)]
    activitytype = activity[0]
    activityname = activity[1]
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType[activitytype], name=activityname))
    quit()

bot.run(open("data/token.txt", "rt").read(), bot=True, reconnect=True)
