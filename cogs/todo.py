import json
import os
import random

from datetime import datetime

from discord.ext import commands
from data.extdata import get_language_str
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
                await ctx.reply(get_language_str(ctx.guild.id, 97))
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
                    await ctx.reply(get_language_str(ctx.guild.id, 98))
                    return
                new_todo = {
                    'desc': desc,
                    'time': datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                }
                tododata.append(new_todo)
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply(get_language_str(ctx.guild.id, 99))
                return
            elif action in remove:
                # this works, i'm already broken mentally.
                if not desc:
                    await ctx.reply(get_language_str(ctx.guild.id, 100))
                    return
                elif not desc.isdigit():
                    await ctx.reply(get_language_str(ctx.guild.id, 101))
                    return
                    # hello your computer has virus
                desc = int(desc) - 1
                # So now it's a valid looking index!
                try:
                    toremove = tododata[desc]
                except IndexError:
                    await ctx.reply(get_language_str(ctx.guild.id, 102))
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
                await ctx.send(get_language_str(ctx.guild.id, 103), embed=embed)

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
                tododata = [x for x in tododata if x != toremove]
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply(get_language_str(ctx.guild.id, 104))
                return
            elif action == 'edit':
                if not desc:
                    await ctx.reply(get_language_str(ctx.guild.id, 105))
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
                await ctx.send(get_language_str(ctx.guild.id, 106), embed=embed)

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
                with open(f"data/todo/{ctx.author.id}.json", 'w+', newline="\n", encoding='utf-8') as todofile:
                    tododata[index] = new_todo
                    json.dump(tododata, todofile)
                    todofile.close()
                await ctx.reply(get_language_str(ctx.guild.id, 107))
                return
            elif action in guildaction:
                if not ctx.author.guild_permissions.manage_messages:
                    await ctx.send(get_language_str(ctx.guild.id, 108))
                    return
                try:
                    with open(f"data/servers/{ctx.guild.id}/todo.json", newline="\n", encoding='utf-8') as todofile:
                        tododata = json.load(todofile)
                except FileNotFoundError:
                    with open(f"data/servers/{ctx.guild.id}/todo.json", "w+", newline="\n", encoding='utf-8') as \
                            todofile:
                        json.dump([], todofile)
                    tododata = []
                if not desc:
                    # check guild todos
                    if tododata:
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
                                with open(f"data/servers/{ctx.guild.id}/todo.json", 'w+', newline="\n",
                                          encoding='utf-8') as todofile:
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
                    else:
                        await ctx.reply("There's nothing in the guild's to-do list.")
                        return
                if desc.isdigit():
                    desc = int(desc) - 1
                    try:
                        toremove = tododata[desc]
                    except IndexError:
                        await ctx.reply(get_language_str(ctx.guild.id, 102))
                        return
                    if toremove.get('author') != ctx.author.id:
                        await ctx.reply(get_language_str(ctx.guild.id, 109))
                        return
                    tododata = [x for x in tododata if x != toremove]
                    if len(tododata) == 0:
                        os.remove(f"data/servers/{ctx.guild.id}/todo.json")
                    else:
                        with open(f"data/servers/{ctx.guild.id}/todo.json", "w+", newline="\n", encoding='utf-8') as \
                                todofile:
                            json.dump(tododata, todofile)
                            todofile.close()
                    await ctx.reply(get_language_str(ctx.guild.id, 104))
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
                    await ctx.reply(get_language_str(ctx.guild.id, 99))
        return


def setup(bot):
    bot.add_cog(Todo(bot))
