import discord
from discord.ext import commands
from data.extdata import get_language_str
import random
import json
import os

from drop.moderation import get_rules, pop_rule, set_rule
from drop.errors import NoRulesError, BrokenRulesError

with open("data/embed_colors.json") as f:
    colors = json.load(f)
    color_list = [c for c in colors.values()]


class Rules(commands.Cog):
    """
    Commands that are all about the server's rules.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(
        name='rules',
        description='Prints a specific rule.',
        usage='3',
        aliases=['rule'],
        brief='Prints a server rule'
    )
    async def rules_command(self, ctx, rule: str):
        try:
            rule_desc = get_rules(ctx.guild.id).get(rule.lower())
        except NoRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 65))
            return
        except BrokenRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 123))
            return
        if not rule_desc:
            await ctx.reply(get_language_str(ctx.guild.id, 66).format(ctx.message.author.name))
            return

        embed = discord.Embed(
            title=f"Rule {rule.lower()}",
            description=f"{rule_desc}",
            color=random.choice(color_list)
        )
        embed.set_author(
            name=ctx.message.author.name,
            icon_url=ctx.message.author.avatar_url,
            url=f"https://discord.com/users/{ctx.message.author.id}/"
        )

        await ctx.reply(
            embed=embed,
            content=None
        )

    @rules_command.error
    async def rules_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rule':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
                return

    @commands.command(
        name='set_rule',
        description='Sets a new rule. Can also edit an already existing rule',
        usage='5a\n(as part of a separate message) no nsfw!!!!1!',
        aliases=['addrule', 'newrule', 'editrule', 'edit_rule', 'setrule'],
        brief='Set a rule to the server.'
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def addrule_command(self, ctx, rulekey):
        def check(ms):
            return ms.channel == ctx.message.channel and ms.author == ctx.message.author

        await ctx.send(get_language_str(ctx.guild.id, 68))
        replymsg = await self.bot.wait_for('message', check=check)
        rulevalue = replymsg.content
        try:
            set_rule(ctx.guild.id, rulekey, rulevalue)
        except BrokenRulesError:
            await ctx.reply(get_language_str(ctx.guild.id, 123))
            return

        await ctx.reply(get_language_str(ctx.guild.id, 69))
        # hghghgh funny number please help its 9:40 pm im fucking tired
        # hey past self, i just want you to know you're a champ for going through this hassle. you're the best. -atlas

    @addrule_command.error
    async def addrule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
                return

    @commands.command(
        name='remove_rule',
        description='Remove a rule',
        usage='5a',
        aliases=['rmrule', 'delrule', 'deleterule', 'delete_rule', 'poprule'],
        brief='Remove a rule for the server'
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def poprule_command(self, ctx, rulekey):
        rulefile = f'data/servers/{ctx.guild.id}/rules.json'
        if not os.path.exists(rulefile):
            await ctx.reply(get_language_str(ctx.guild.id, 70))
            return

        try:
            pop_rule(ctx.guild.id, rulekey)
        except KeyError:
            await ctx.reply(get_language_str(ctx.guild.id, 71))
            return

        await ctx.reply(get_language_str(ctx.guild.id, 72))

    @poprule_command.error
    async def poprule_handler(self, ctx, error):
        if isinstance(error, commands.MissingRequiredArgument):
            if error.param.name == 'rulekey':
                await ctx.reply(get_language_str(ctx.guild.id, 67).format(ctx.message.author.name))
                return


def setup(bot):
    bot.add_cog(Rules(bot))
    # Adds the Basic commands to the bot
    # Note: The "setup" function has to be there in every cog file
