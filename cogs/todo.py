import random

from discord.ext import commands
from data.extdata import get_language_str, wait_for_user
import discord

from drop.todo import *

# These color constants are taken from discord.js library
with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


rm_aliases = ['rm', 'r', 'del', 'd', 'delete']
edit_aliases = ['e', 'ed']
add_aliases = ['a']


class Todo(commands.Cog):
    """
    Just regular, to-do notes for the user and guild.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="todo",
        description="The to-do command. This is a command group that has many different commands inside, "
                    "notably \"add\", \"delete\", \"remove\", and other subcommands in \"todo guild\"",
        brief="Basic to-do subcommands",
        usage="add Bite my own tongue"
    )
    async def todo_group(self, ctx):
        if not ctx.invoked_subcommand:
            # User just wanted to check their current to-do stuff.
            todo_data = get_todos(ctx.author.id)
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
            return

    @todo_group.command(
        name="add",
        aliases=add_aliases,
        brief="Add things to your to-do list",
        usage="Bake a cake for tomorrow"
    )
    async def add_todo_command(ctx, *, user_args):
        add_todo(ctx.author.id, user_args)
        await ctx.reply(get_language_str(ctx.guild.id, 99))
        return
    
    @todo_group.command(
        name="remove",
        aliases=rm_aliases,
        brief="Remove things from your to-do list",
        usage="1"
    )
    async def remove_todo_command(self, ctx, index):
        index = int(index) - 1
        # So now it's a valid looking index!
        try:
            to_remove = get_todos(ctx.author.id)[index]
        except IndexError:
            await ctx.reply(get_language_str(ctx.guild.id, 102))
            return
        embed = discord.Embed(
            title=f"Item {index + 1}",
            description=f"{to_remove['desc']}\n"
                        f"*{to_remove['time']}*",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        msg = await ctx.send(get_language_str(ctx.guild.id, 103), embed=embed)

        if await wait_for_user(ctx, self.bot, msg):
            rm_todo(ctx.author.id, index)  # shouldn't raise an error since we know that to-do already exists
            await ctx.reply(get_language_str(ctx.guild.id, 104))
        return

    @todo_group.command(
        name="edit",
        aliases=edit_aliases,
        brief="Edit things from your to-do list",
        usage="1 Throw away the cake for tomorrow"
    )
    async def edit_todo_command(self, ctx, index, *, user_args):
        if not index.isdigit(): return

        index = int(index) - 1
        if not user_args:
            await ctx.reply(get_language_str(ctx.guild.id, 124))
            return
        embed = discord.Embed(
            title=f"Item {index + 1}",
            description=f"{user_args}\n"
                        f"*{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        msg = await ctx.send(get_language_str(ctx.guild.id, 106), embed=embed)

        if await wait_for_user(ctx, self.bot, msg):
            edit_todo(ctx.author.id, index, user_args)
            await ctx.reply(get_language_str(ctx.guild.id, 107))
            return

    @todo_group.group(
        name="guild",
        brief="Command group for guild-specific to-do lists",
        usage="add Remove #general"
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def guild_todo_group(self, ctx):
        if not ctx.invoked_subcommand:
            # check guild todos
            todo_data = get_guild_todos(ctx.guild.id)
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

    @guild_todo_group.command(
        name="add",
        aliases=add_aliases,
        brief="Add things to the guild's to-do list",
        usage="Delete server"
    )
    async def add_todo_command(self, ctx, *, user_args):
        add_guild_todo(ctx.guild.id, user_args, ctx.author.id)
        await ctx.reply(get_language_str(ctx.guild.id, 99))
        return

    @guild_todo_group.command(
        name="remove",
        aliases=rm_aliases,
        brief="Remove things from the guild's to-do list",
        usage="1"
    )
    async def remove_guild_todo_command(self, ctx, index):
        desc = int(index) - 1
        try:
            to_remove = get_guild_todos(ctx.guild.id)[desc]
        except IndexError:
            await ctx.reply(get_language_str(ctx.guild.id, 102))
            return
        if to_remove.get('author') != ctx.author.id:
            await ctx.reply(get_language_str(ctx.guild.id, 109))
            return

        rm_guild_todo(ctx.guild.id, desc)
        await ctx.reply(get_language_str(ctx.guild.id, 104))
        return

    @guild_todo_group.command(
        name="edit",
        aliases=edit_aliases,
        brief="Edit things from the guild's to-do list",
        usage="1 Archive this server instead"
    )
    async def edit_guild_todo_command(self, ctx, index, *, user_args):
        if not index.isdigit(): return
        index = int(index) - 1

        if not user_args:
            await ctx.reply(get_language_str(ctx.guild.id, 124))
            return

        try:
            to_edit = get_guild_todos(ctx.guild.id)[index]
        except IndexError:
            await ctx.reply(get_language_str(ctx.guild.id, 102))
            return

        if to_edit.get('author') != ctx.author.id:
            await ctx.reply(get_language_str(ctx.guild.id, 109))
            return

        embed = discord.Embed(
            title=f"Item {index + 1}",
            description=f"{user_args}\n"
                        f"*{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}*",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )
        msg = await ctx.send(get_language_str(ctx.guild.id, 106), embed=embed)

        if await wait_for_user(ctx, self.bot, msg):
            edit_guild_todo(ctx.guild.id, index, user_args)
            await ctx.reply(get_language_str(ctx.guild.id, 107))
            return


def setup(bot):
    bot.add_cog(Todo(bot))
