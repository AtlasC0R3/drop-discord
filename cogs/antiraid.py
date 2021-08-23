import random
import re

from discord.ext import commands
import discord

from drop.config import *

from data.extdata import wait_for_user

from typing import Optional


default_antiraid_config = {'enabled': False, 'invite': False, 'messages': [], 'channel': 0}


def get_antiraid_config(guild_id=int):
    try:
        antiraid_config = get_server_config(guild_id, 'antiraid')
    except ConfigParameterNotFound:
        antiraid_config = default_antiraid_config
        write_server_config(guild_id, 'antiraid', antiraid_config)
    for key in default_antiraid_config:
        if key not in antiraid_config.keys():
            antiraid_config[key] = default_antiraid_config[key]
    return antiraid_config


def find_invite_by_code(invite_list, code):
    # Simply looping through each invite in an
    # invite list which we will get using guild.invites()
    for inv in invite_list:
        # Check if the invite code in this element
        # of the list is the one we're looking for
        if inv.code == code:
            # If it is, we return it.
            return inv


def parse_arg_lists(argument=None):
    if argument.startswith("\"") and argument.endswith("\""):
        return re.compile("\"(.*?)\"").findall(argument)
    elif argument:
        return [argument]
    else:
        return []


def get_raid_embed(guild: discord.Guild, custom_message: str):
    description = "It's against the [Community Guidelines](https://discord.com/guidelines/) " \
                  "to raid servers, thus against the " \
                  "[Terms of Service](https://discord.com/guidelines/). It's okay to not agree with a " \
                  "specific community or server, but please don't harass that community, instead " \
                  "try to peacefully resolve the problem, or ignore them.\n" \
                  "*I'm just a bot sending an automated message, I don't know anything. This was sent " \
                  "because the server you tried to join had anti-raid enabled. " \
                  "Sorry if this was a mistake.*"
    # Hey for once I actually support Discord's ToS. Seriously, fuck Discord.
    # The only thing I really agree with is their privacy policy and their community guidelines.
    # The rest is just a big "NO." Anyway, anti-discord-pro-matrix.org asides, that's done.

    if custom_message:
        description = f"```{custom_message}```\n{description}"

    return discord.Embed(
        description=description
    ).set_author(
        name=guild.name,
        icon_url=guild.icon_url
    )


class Antiraid(commands.Cog, name="Antiraid"):
    """
    General antiraid-related commands.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.group(
        name="antiraid",
        description="Prevents anyone to join. If they do join, they get banned and receive a DM basically saying "
                    "that it's against Discord's ToS to raid servers.\n"
                    "An administrator can also set a specific invite to ban, in case raiders are only using "
                    "one specific invite.",
        brief="Configure Drop's anti-raid functions"
    )
    async def antiraid_group(self, ctx):
        if not ctx.invoked_subcommand:
            # return status
            antiraid_config = get_antiraid_config(ctx.guild.id)
            invite = antiraid_config['invite']
            channel = antiraid_config['channel']
            embed = discord.Embed(
                title="Anti-raid status",
                description=f"Enabled: **{'Yes' if antiraid_config['enabled'] else 'No'}**\n"
                            f"Raid invite: **{invite if invite else 'Not configured'}**\n"
                            f"Announcement channel: **{f'<#{channel}>' if channel else 'Not specified'}**\n"
            )
            embed.set_author(
                name=ctx.guild.name,
                icon_url=ctx.guild.icon_url
            )
            if antiraid_config['messages']:
                value = ""
                for x in antiraid_config['messages']:
                    value += f"```{x}```\n"
                embed.add_field(
                    name='Custom messages',
                    value=value
                )
            await ctx.reply(embed=embed)
            return

    @antiraid_group.command(
        name="toggle",
        description="Toggles whether anti-raid will be on or off. If on, it's strongly advised not to join the server. "
                    "If off, it should be safe to join.",
        # Then again, if you're someone who constantly leaves and rejoins the server, why? Who does that?!
        brief="Toggles whether anti-raid will be on or off"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def toggle_antiraid_command(self, ctx):
        antiraid_config = get_antiraid_config(ctx.guild.id)
        status = antiraid_config['enabled']
        if status:
            # disable
            antiraid_config['enabled'] = False
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Alright, anti-raid has been disabled. *People can safely join now.*')
        else:
            # enable
            antiraid_config['enabled'] = True
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Okay, anti-raid has been enabled. *I\'d advise everyone not to join for now.*')

    @antiraid_group.command(
        name="invite",
        description="In case raiders are using a specific invite, Drop can automatically adapt to "
                    "only ban new members that used the invite.",
        brief="Sets the invite code that raiders use",
        usage="xY7dgUYfhgf (alternatively could be used without any arguments to ban to reset invite configurations)"
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def invite_antiraid_command(self, ctx, invite: Optional[discord.Invite] = None):
        antiraid_config = get_antiraid_config(ctx.guild.id)
        if invite:
            antiraid_config['invite'] = invite.id
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Successfully set the invite configuration.')
        else:
            antiraid_config['invite'] = False
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Successfully reset the invite configuration.')

    @antiraid_group.command(
        name="setmessage",
        description="Sets a custom message (or messages) on the ban notice that is sent to raiders.",
        brief="Sets the messages used in the ban notice",
        usage="\"don't do that again please\" \"just let it die\" \"haha skill issue lmao\"\n(you could also "
              "specify only one message by just doing \"antiraid setmessage dont do that again please i beg you\")",
        aliases=['message']
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def message_antiraid_command(self, ctx, *, messages=None):
        antiraid_config = get_antiraid_config(ctx.guild.id)
        if not messages:
            msg = await ctx.send("Are you sure you want to erase the custom messages? This is what the "
                                 "ban notice will now look like.",
                                 embed=get_raid_embed(ctx.guild, messages))
            if await wait_for_user(ctx, self.bot, msg):
                antiraid_config['messages'] = []
                write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
                await ctx.reply("Alright, custom messages have been erased.")
                return
        else:
            messages = parse_arg_lists(messages)
        if messages:
            if len(messages) > 1:
                custom_message = random.choice(messages)
            else:
                custom_message = messages[0]
        else:
            custom_message = ""
        embed = get_raid_embed(ctx.guild, custom_message)
        msg = await ctx.send("This is what the ban notice will look like. Are you sure?", embed=embed)
        if await wait_for_user(ctx, self.bot, msg):
            antiraid_config['messages'] = messages
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply("Alright, custom messages have been set.")

    @antiraid_group.command(
        name="channel",
        description="If set, all ban notices are going to be sent there.",
        brief="Sends antiraid notice in the specified channel",
        usage="#hall-of-dumbasses",
        aliases=['setchannel']
    )
    @commands.has_guild_permissions(manage_guild=True)
    async def antiraid_setchannel_command(self, ctx, *, channel: Optional[discord.TextChannel] = None):
        antiraid_config = get_antiraid_config(ctx.guild.id)
        if channel:
            antiraid_config['channel'] = channel.id
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Alright, all ban notices will be sent in that channel.')
        else:
            antiraid_config['channel'] = 0
            write_server_config(ctx.guild.id, 'antiraid', antiraid_config)
            await ctx.reply('Sure, no public messages will be sent about anyone getting banned.')

    @commands.Cog.listener()
    async def on_member_join(self, member):
        antiraid_config = get_antiraid_config(member.guild.id)
        if antiraid_config['enabled']:
            reason = None
            invite_nonsense = antiraid_config['invite']
            announcement_channel = antiraid_config['channel']
            if invite_nonsense:
                invites_before_join = self.bot.guild_invites[member.guild.id]
                invites_after_join = await member.guild.invites()
                for invite in invites_before_join:
                    if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:
                        self.bot.guild_invites[member.guild.id] = invites_after_join
                        if invite.code == invite_nonsense:
                            # await member.ban(reason="WOW YOU GOT THE TETRIS! WOW YOU'RE THE BEST! "
                            #                         "WOOOOOO! WOOOOOOOOOOOOO! TETRIIIIIIIIIIIIIIIIS!")
                            reason = "Joined using an invite that was specified as a raided invite. " \
                                     f"If this was unintended, please use " \
                                     f"\"{self.bot.user.mention} antiraid toggle\" " \
                                     "to disable antiraid mode, or specify another invite to block using " \
                                     f"\"{self.bot.user.mention} antiraid invite (insert invite)\"."
            else:
                reason = "Joined while anti-raid was enabled. " \
                         f"If this was unintended, please use \"{self.bot.user.mention} antiraid toggle\" " \
                         "to disable antiraid mode, or specify an invite to block using " \
                         f"\"{self.bot.user.mention} antiraid invite (insert invite)\"."
            if reason:
                custom_messages = antiraid_config['messages']
                custom_message = ""
                if custom_messages:
                    if len(custom_messages) > 1:
                        custom_message = random.choice(custom_messages)
                    else:
                        custom_message = custom_messages[0]
                await member.send(embed=get_raid_embed(member.guild, custom_message))
                await member.ban(reason=reason)

                description = f"**{member}**, *most likely* a server raider, has been banned."
                if custom_message:
                    description = f"```{custom_message}```\n{description}"

                if announcement_channel:
                    channel = member.guild.get_channel(announcement_channel)
                    await channel.send(embed=discord.Embed(
                        description=description
                    ).set_author(
                        name=member.guild.name,
                        icon_url=member.guild.icon_url
                    ).set_thumbnail(
                        url=member.avatar_url
                    ))

    @commands.Cog.listener()
    async def on_invite_create(self, invite):
        if invite.guild.id in self.bot.guild_invites:
            invites = await invite.guild.invites()  # get a list of invites from the guild
            self.bot.guild_invites[invite.guild.id] = invites  # store the guild's invites internally

    @commands.Cog.listener()
    async def on_invite_delete(self, invite):
        if invite.guild.id in self.bot.guild_invites:
            invites = await invite.guild.invites()  # get a list of invites from the guild
            self.bot.guild_invites[invite.guild.id] = invites  # store the guild's invites internally
        if get_antiraid_config(invite.guild.id)['invite'] == invite.id:
            config = get_antiraid_config(invite.guild.id)
            config['invite'] = False
            write_server_config(invite.guild.id, 'antiraid', config)


def setup(bot):
    bot.add_cog(Antiraid(bot))
