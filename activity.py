import discord
import json


class MyClient(discord.Client):
    async def on_ready(self):
        with open("data/activities.json", encoding='utf-8', newline="\n") as f:
            activities = json.load(f)
        activitynumber = input('Please input your activity index:\n')
        try:
            activity = list(activities)[int(activitynumber)]
        except IndexError:
            exit("That wasn't a valid index. Rather than running again I'm aborting now.\n"
                 "Make sure you inputted your values correctly.")
            return
        activitytype = activity[0]
        activityname = activity[1]
        await client.change_presence(activity=discord.Activity(type=discord.ActivityType[activitytype],
                                                               name=activityname))
        exit(1)


client = MyClient()
client.run(open("data/token.txt", "rt").read(), bot=True, reconnect=False)
