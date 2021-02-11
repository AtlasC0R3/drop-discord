import json
import os
import random

from datetime import datetime

from discord.ext import commands
import discord

# These color constants are taken from discord.js library
with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Todo(commands.Cog):
    """
    Basic to-do commands
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='todo',
        description='Basic to-do command that is user-specific, and that should also be cross-server.',
        brief='User-specific todo command'
    )
    async def todo_command(self, ctx, action=None, *, desc=None):
        if not os.path.exists("data/todo/"):
            os.makedirs("data/todo/")
        try:
            with open(f"data/todo/{ctx.author.id}.json", newline="\n", encoding='utf-8') as todofile:
                tododata = json.load(todofile)
                # does the user have to-do stuff
                # oh god pycharm things to-do without '-' is always a to-do thing to do
        except FileNotFoundError:
            # nothing generated yet
            with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                tododata = []
                json.dump(tododata, todofile)
        if not action:
            # User just wanted to check their current to-do stuff.
            if not tododata:
                await ctx.reply("You don't have anything. So, why not kick back and relax?")
                return
            embed = discord.Embed(
                title="To-do list",
                color=random.choice(color_list)
            )
            embed.set_author(
                name=ctx.message.author.name,
                icon_url=ctx.message.author.avatar_url,
                url=f"https://discord.com/users/{ctx.message.author.id}/"
            )
            for idx, todo in enumerate(tododata):
                desc = todo['desc']
                time = todo['time']
                embed.add_field(
                    name=f'Item {idx + 1}',
                    value=f'{desc}\n'
                          f'*{time}*',
                    inline=True
                )
            await ctx.reply('Here\'s your to-do list', embed=embed)
        else:
            action = action.lower()

            def check(ms):
                return ms.channel == ctx.message.channel and ms.author == ctx.message.author

            remove = ['del', 'remove', 'rm']
            guildaction = ['guild', 'server']
            if action == 'add':
                if not desc:
                    await ctx.reply("I'd like to add stuff to your to-do list, but you gotta tell me *what* to add!")
                    return
                new_todo = {
                    'desc': desc,
                    'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                tododata.append(new_todo)
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply("Successfully added.")
                return
            elif action in remove:
                # this works, i'm already broken mentally.
                if not desc:
                    await ctx.reply("I'd like to remove stuff from your to-do list, but you gotta tell me *what* to "
                                    "remove!")
                    return
                elif not desc.isdigit():
                    await ctx.reply("You need to specify the **number** of the item in the list"
                                    " that you wish to remove!")
                    return
                    # hello your computer has virus
                desc = int(desc) - 1
                # So now it's a valid looking index!
                try:
                    toremove = tododata[desc]
                except IndexError:
                    await ctx.reply("That item does not exist.")
                    return
                embed = discord.Embed(
                    title=f"Item {desc + 1}",
                    description=f"{toremove['desc']}\n"
                                f"*{toremove['time']}*",
                    color=random.choice(color_list)
                )
                embed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.avatar_url,
                    url=f"https://discord.com/users/{ctx.message.author.id}/"
                )
                await ctx.send("Are you sure you want to remove this?", embed=embed)

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
                tododata = [x for x in tododata if x != toremove]
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply("Successfully removed.")
                return
            elif action == 'edit':
                if not desc:
                    await ctx.reply("I'd like to edit stuff, but you gotta tell me *what* to modify!")
                    return
                desc = desc.split(' ')
                index = int(desc[0]) - 1
                desc = ' '.join(desc[1:])
                new_todo = {
                    'desc': desc,
                    'time': datetime.now().strftime('%d/%m/%Y %H:%M:%S')
                }
                embed = discord.Embed(
                    title=f"Item {index + 1}",
                    description=f"{new_todo['desc']}\n"
                                f"*{new_todo['time']}*",
                    color=random.choice(color_list)
                )
                embed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.avatar_url,
                    url=f"https://discord.com/users/{ctx.message.author.id}/"
                )
                await ctx.send("Are you sure you want to edit this?", embed=embed)

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
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    tododata[index] = new_todo
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply("Successfully edited.")
                return
            elif action in guildaction:
                if not ctx.author.guild_permissions.manage_messages:
                    await ctx.send("You don't have the permissions to do that!")
                    return
                with open(f"data/servers/{ctx.guild.id}/todo.json", newline="\n", encoding='utf-8') as todofile:
                    tododata = json.load(todofile)
                if not desc:
                    # check guild todos
                    embed = discord.Embed(
                        title="Guild to-do list",
                        color=random.choice(color_list)
                    )
                    embed.set_author(
                        name=ctx.message.author.name,
                        icon_url=ctx.message.author.avatar_url,
                        url=f"https://discord.com/users/{ctx.message.author.id}/"
                    )
                    for idx, todo in enumerate(tododata):
                        desc = todo['desc']
                        time = todo['time']
                        author = ctx.guild.get_member(todo['author'])
                        if not author:
                            tododata.pop(idx)
                            with open(f"data/servers/{ctx.guild.id}/todo.json", 'w+', newline="\n", encoding='utf-8') \
                                    as todofile:
                                json.dump(tododata, todofile)
                                break
                        else:
                            author = author.name
                        embed.add_field(
                            name=f'Item {idx + 1}',
                            value=f'{desc}\n'
                                  f'*{time}, authored by {author}*',
                            inline=True
                        )
                    await ctx.reply(embed=embed)
                    return
                if desc.isdigit():
                    desc = int(desc) - 1
                    try:
                        toremove = tododata[desc]
                    except IndexError:
                        await ctx.reply("That item does not exist.")
                        return
                    if toremove.get('author') != ctx.author.id:
                        await ctx.reply("You don't appear to be the author of that note, which unfortunately means you "
                                        "cannot remove that note.")
                        return
                    tododata = [x for x in tododata if x != toremove]
                    with open(f"data/servers/{ctx.guild.id}/todo.json", 'w+', newline="\n", encoding='utf-8') as \
                            todofile:
                        json.dump(tododata, todofile)
                        todofile.close()
                    await ctx.reply("Successfully removed.")
                    return
                else:
                    new_todo = {
                        'desc': desc,
                        'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
                        'author': ctx.author.id
                    }
                    tododata.append(new_todo)
                    with open(f"data/servers/{ctx.guild.id}/todo.json", 'w+', newline="\n", encoding='utf-8') as \
                            todofile:
                        json.dump(tododata, todofile)
                        todofile.close()
                    await ctx.reply("Successfully added.")
        return

    @todo_command.error
    async def todo_handler(self, ctx, error):
        await ctx.send(error)


def setup(bot):
    bot.add_cog(Todo(bot))
