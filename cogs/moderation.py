import ast
import time
import json
import random
import os

import discord
from discord.ext import commands

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='purge',
        description='Deletes a certain amount of messages.',
        usage='5',
        brief='Deletes a set amount of messages'
    )
    @commands.has_guild_permissions(manage_messages=True)
    async def purge_command(self, ctx, to_delete=5):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(f"[{ctx.author.name}], are you sure you want to delete [{to_delete}] messages?")
        msg = await self.bot.wait_for('message', check=check)
        reply = msg.content.lower()  # Set the confirmation
        if reply in ('y', 'yes', 'confirm'):
            await ctx.channel.purge(limit=to_delete + 3)
            temp_message = await ctx.send(f"[{ctx.author.name}], deleted [{to_delete}] messages.")
            time.sleep(5)
            await temp_message.delete()
            return
        elif reply in ('n', 'no', 'cancel', 'flanksteak'):  # idk why i decided to put flanksteak there
            await ctx.send("Alright, action cancelled.")
            return
        else:
            await ctx.send("I have no idea what you want me to do. Action cancelled.")
            return

    @commands.command(
        name='rules',
        description='Prints a specific rule.',
        usage='3',
        aliases=['rule'],
        brief='Prints a server rule'
    )
    async def rules_command(self, ctx, rule: str):
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        try:
            open(rulefile, 'r', newline="\n", encoding="utf-8")
        except FileNotFoundError:
            await ctx.send("I have found no rules for this server.")
            return

        rules = json.load(open(rulefile, "r", encoding="utf-8", newline="\n"))

        rule_desc = rules.get(rule.lower())
        if rule_desc is None:
            await ctx.send(f"[{ctx.message.author.name}], you specified an invalid rule.")
            return

        embed = discord.Embed(
            title=f"Rule {rule}",
            description=f"{rule_desc}",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        await ctx.send(
            embed=embed,
            content=None
        )

    @rules_command.error
    async def rules_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rule':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule.")
                return

    @commands.command(
        name='set_rule',
        description='Sets a new rule. Can also edit an already existing rule',
        usage='5a\n(as part of a separate message) no nsfw!!!!1!',
        aliases=['addrule', 'newrule', 'editrule', 'edit_rule', 'setrule'],
        brief='Add a rule to the server.'
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def addrule_command(self, ctx, rulekey):
        rulepath = 'data/servers/' + str(ctx.guild.id) + '/'
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        if not os.path.exists(rulepath):
            os.makedirs(rulepath)
        if os.path.exists(rulefile):
            ruledata = json.load(open(rulefile, encoding="utf-8", newline="\n"))
        else:
            ruledata = {}

        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send("What shall be the rule description?")
        replymsg = await self.bot.wait_for('message', check=check)
        rulevalue = replymsg.content
        ruledata[rulekey.lower()] = rulevalue

        json.dump(ruledata, open(rulefile, 'w+', newline='\n', encoding="utf-8"), indent=2)

        await ctx.send("Success, rule has been added.")

    @addrule_command.error
    async def addrule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule name.")
                return

    @commands.command(
        name='remove_rule',
        description='Remove a rule',
        usage='5a',
        aliases=['rmrule', 'delrule', 'deleterule', 'delete_rule', 'poprule'],
        brief='Remove a rule for the server'
    )
    async def poprule_command(self, ctx, rulekey):
        rulefile = 'data/servers/' + str(ctx.guild.id) + '/rules.json'
        if not os.path.exists(rulefile):
            await ctx.send("There are no rules for this server.")
            return

        with open(rulefile, 'r+', newline="\n", encoding="utf-8") as rulefileobject:
            ruledata = json.load(rulefileobject)
            try:
                ruledata.pop(rulekey.lower())
            except KeyError:
                await ctx.send("The specified rule does not exist.")
                rulepopped = False
            else:
                rulepopped = True
            if ruledata == {}:
                rulefileobject.close()
                os.remove(rulefile)
            else:
                json.dump(ruledata, open(rulefile, 'w+', newline='\n', encoding='utf-8'), indent=2)
                rulefileobject.close()

        if rulepopped:
            await ctx.send("Success, rule has been deleted.")

    @poprule_command.error
    async def poprule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.send(f"[{ctx.message.author.name}], you did not specify a rule name.")
                return


def setup(bot):
    bot.add_cog(Moderation(bot))
