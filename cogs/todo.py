import random

from discord.ext import commands
from data.extdata import get_language_str
import discord

from drop.todo import *

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
    async def todo_command(self, ctx, *, user_args=None):
        todo_data = get_todos(ctx.author.id)
        if not user_args:
            # User just wanted to check their current to-do stuff.
            if not todo_data:
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
            for idx, todo in enumerate(todo_data):
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
            # We have to do something
            action = user_args.lower().replace('\n', ' ').split(' ')[0]

            def check(ms):
                return ms.channel == ctx.message.channel and ms.author == ctx.message.author
            guild_action = ['guild', 'server']
            if not action.isdigit():
                desc = ' '.join(user_args.replace('\n', ' ').split(' ')[1:])
                try:
                    single_desc = ' '.join(user_args.split(' ')[1])
                    add_args = ' '.join(user_args.split(' ')[2:])
                except IndexError:
                    single_desc = None
                    add_args = None
                if user_args.lower().startswith('edit ') and single_desc.isdigit():
                    index = int(desc[0]) - 1
                    if not add_args:
                        await ctx.reply(get_language_str(ctx.guild.id, 124))
                        return
                    embed = discord.Embed(
                        title=f"Item {index + 1}",
                        description=f"{add_args}\n"
                                    f"*{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*",
                        color=random.choice(color_list)
                    )
                    embed.set_author(
                        name=ctx.message.author.name,
                        icon_url=ctx.message.author.avatar_url,
                        url=f"https://discord.com/users/{ctx.message.author.id}/"
                    )
                    await ctx.send(get_language_str(ctx.guild.id, 106), embed=embed)

                    reply_msg = await self.bot.wait_for('message', check=check)
                    reply = reply_msg.content.lower()
                    if reply in ('y', 'yes', 'confirm'):
                        pass
                    elif reply in ('n', 'no', 'cancel', 'flanksteak'):
                        await ctx.send(get_language_str(ctx.guild.id, 26))
                        return
                    else:
                        await ctx.send(get_language_str(ctx.guild.id, 27))
                        return
                    edit_todo(ctx.author.id, index, add_args)
                    await ctx.reply(get_language_str(ctx.guild.id, 107))
                    return
                elif action in guild_action:
                    if not ctx.author.guild_permissions.manage_messages:
                        await ctx.send(get_language_str(ctx.guild.id, 108))
                        return
                    todo_data = get_guild_todos(ctx.guild.id)
                    if not desc:
                        # check guild todos
                        if todo_data:
                            embed = discord.Embed(
                                title="Guild to-do list",
                                color=random.choice(color_list)
                            )
                            embed.set_author(
                                name=ctx.message.author.name,
                                icon_url=ctx.message.author.avatar_url,
                                url=f"https://discord.com/users/{ctx.message.author.id}/"
                            )
                            for idx, todo in enumerate(todo_data):
                                desc = todo['desc']
                                time = todo['time']
                                author = ctx.guild.get_member(todo['author'])
                                if not author:
                                    rm_guild_todo(ctx.guild.id, idx)
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
                            await ctx.reply(get_language_str(ctx.guild.id, 125))
                            return
                    if desc.isdigit():
                        desc = int(desc) - 1
                        try:
                            to_remove = todo_data[desc]
                        except IndexError:
                            await ctx.reply(get_language_str(ctx.guild.id, 102))
                            return
                        if to_remove.get('author') != ctx.author.id:
                            await ctx.reply(get_language_str(ctx.guild.id, 109))
                            return
                        rm_guild_todo(ctx.guild.id, desc)
                        await ctx.reply(get_language_str(ctx.guild.id, 104))
                        return
                    else:
                        add_guild_todo(ctx.guild.id, desc, ctx.author.id)
                        await ctx.reply(get_language_str(ctx.guild.id, 99))
                        return

                # we have to add something
                add_todo(ctx.author.id, user_args)
                await ctx.reply(get_language_str(ctx.guild.id, 99))
                return
            elif action.isdigit():
                desc = int(user_args) - 1
                # So now it's a valid looking index!
                try:
                    to_remove = todo_data[desc]
                except IndexError:
                    await ctx.reply(get_language_str(ctx.guild.id, 102))
                    return
                embed = discord.Embed(
                    title=f"Item {desc + 1}",
                    description=f"{to_remove['desc']}\n"
                                f"*{to_remove['time']}*",
                    color=random.choice(color_list)
                )
                embed.set_author(
                    name=ctx.message.author.name,
                    icon_url=ctx.message.author.avatar_url,
                    url=f"https://discord.com/users/{ctx.message.author.id}/"
                )
                await ctx.send(get_language_str(ctx.guild.id, 103), embed=embed)

                reply_msg = await self.bot.wait_for('message', check=check)
                reply = reply_msg.content.lower()
                if reply in ('y', 'yes', 'confirm'):
                    pass
                elif reply in ('n', 'no', 'cancel', 'flanksteak'):
                    await ctx.send(get_language_str(ctx.guild.id, 26))
                    return
                else:
                    await ctx.send(get_language_str(ctx.guild.id, 27))
                    return
                rm_todo(ctx.author.id, desc)  # shouldn't raise an error since we know that to-do already exists
                await ctx.reply(get_language_str(ctx.guild.id, 104))
                return
            return


def setup(bot):
    bot.add_cog(Todo(bot))
