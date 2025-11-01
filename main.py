import discord
from discord import app_commands
from discord.ext import commands
from discord.ui import Button, View

OWNER_ID = 1117756512136335370
WELCOME_CHANNEL_ID = 1421496364814045272

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=">", intents=intents, owner_id=OWNER_ID)

@bot.event
async def on_ready():
    print(f"logged in as {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"synced {len(synced)} commands")
    except Exception as e:
        print(e)

@bot.event
async def on_member_join(member):
    channel = bot.get_channel(WELCOME_CHANNEL_ID)
    if channel:
        await channel.send(f"welcome {member.mention} enjoy your stay")

# Slash commands: review and suggest

@bot.tree.command(name="review", description="submit a review")
@app_commands.describe(stars="stars from 1 to 5", message="your review message")
async def review(interaction: discord.Interaction, stars: app_commands.Range[int, 1, 5], message: str):
    embed = discord.Embed(title="new review", description=f"stars {stars}\nmessage {message}", color=discord.Color.yellow())
    await interaction.response.send_message(embed=embed)

@bot.tree.command(name="suggest", description="submit a suggestion")
@app_commands.describe(message="your suggestion message")
async def suggest(interaction: discord.Interaction, message: str):
    embed = discord.Embed(title="new suggestion", description=message, color=discord.Color.blue())

    class AcceptButton(Button):
        def __init__(self):
            super().__init__(label="accept", style=discord.ButtonStyle.green)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != OWNER_ID:
                await interaction.response.send_message("only owner can use this", ephemeral=True)
                return
            embed.set_footer(text="accepted")
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("accepted", ephemeral=True)

    class DeclineButton(Button):
        def __init__(self):
            super().__init__(label="decline", style=discord.ButtonStyle.red)

        async def callback(self, interaction: discord.Interaction):
            if interaction.user.id != OWNER_ID:
                await interaction.response.send_message("only owner can use this", ephemeral=True)
                return
            embed.set_footer(text="declined")
            await interaction.message.edit(embed=embed)
            await interaction.response.send_message("declined", ephemeral=True)

    view = View()
    view.add_item(AcceptButton())
    view.add_item(DeclineButton())

    await interaction.response.send_message(embed=embed, view=view)

# Prefix commands

@bot.command()
@commands.is_owner()
async def say(ctx, channel: discord.TextChannel, *, message: str):
    await channel.send(message)
    await ctx.message.delete()

@bot.command()
@commands.is_owner()
async def help(ctx):
    commands_list = [
        ">kick @user reason - kick a user",
        ">ban @user reason - ban a user",
        ">unban user_id - unban a user",
        ">mute @user minutes reason - mute a user",
        ">unmute @user - unmute a user",
        ">warn @user reason - warn a user",
        ">purge amount - purge messages",
        ">slowmode seconds - set slowmode",
        ">lock - lock the channel",
        ">unlock - unlock the channel",
        ">addrole @user @role - add role",
        ">removerole @user @role - remove role",
        ">nick @user newnick - change nick",
        ">serverinfo - server info",
        ">userinfo @user - user info",
        ">ping - check ping",
        ">invite - create invite",
        ">poll question - create poll",
        ">announce channel message - announce",
        ">prune days - prune members",
        ">voicekick @user - kick from voice",
        ">say channel message - send message",
        ">help - this list"
    ]
    help_msg = "available commands\n" + "\n".join(commands_list)
    await ctx.send(help_msg)

@bot.command()
@commands.is_owner()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason: str = None):
    await member.kick(reason=reason)
    await ctx.send(f"kicked {member.mention} reason {reason}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason: str = None):
    await member.ban(reason=reason)
    await ctx.send(f"banned {member.mention} reason {reason}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user_id: int):
    user = discord.Object(id=user_id)
    await ctx.guild.unban(user)
    await ctx.send(f"unbanned {user_id}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(moderate_members=True)
async def mute(ctx, member: discord.Member, minutes: int, *, reason: str = None):
    duration = discord.utils.utcnow() + discord.utils.timedelta(minutes=minutes)
    await member.timeout(until=duration, reason=reason)
    await ctx.send(f"muted {member.mention} for {minutes} minutes reason {reason}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(moderate_members=True)
async def unmute(ctx, member: discord.Member):
    await member.timeout(until=None)
    await ctx.send(f"unmuted {member.mention}")

@bot.command()
@commands.is_owner()
async def warn(ctx, member: discord.Member, *, reason: str):
    await ctx.send(f"warned {member.mention} reason {reason}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"purged {amount} messages", delete_after=5)

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_channels=True)
async def slowmode(ctx, seconds: int):
    await ctx.channel.edit(slowmode_delay=seconds)
    await ctx.send(f"slowmode set to {seconds} seconds")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_channels=True)
async def lock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = False
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("channel locked")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx):
    overwrite = ctx.channel.overwrites_for(ctx.guild.default_role)
    overwrite.send_messages = None
    await ctx.channel.set_permissions(ctx.guild.default_role, overwrite=overwrite)
    await ctx.send("channel unlocked")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    await member.add_roles(role)
    await ctx.send(f"added {role.name} to {member.mention}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    await member.remove_roles(role)
    await ctx.send(f"removed {role.name} from {member.mention}")

@bot.command()
@commands.is_owner()
@commands.has_permissions(manage_nicknames=True)
async def nick(ctx, member: discord.Member, *, new_nick: str):
    await member.edit(nick=new_nick)
    await ctx.send(f"changed nick of {member.mention} to {new_nick}")

@bot.command()
@commands.is_owner()
async def serverinfo(ctx):
    embed = discord.Embed(title="server info", description=f"name {ctx.guild.name}\nowner {ctx.guild.owner}\nmembers {ctx.guild.member_count}")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title="user info", description=f"name {member}\njoined {member.joined_at}\ncreated {member.created_at}")
    await ctx.send(embed=embed)

@bot.command()
@commands.is_owner()
async def ping(ctx):
    await ctx.send(f"pong latency {round(bot.latency * 1000)}ms")

@bot.command()
@commands.is_owner()
@commands.has_permissions(create_instant_invite=True)
async def invite(ctx):
    invite = await ctx.channel.create_invite()
    await ctx.send(f"invite link {invite.url}")

@bot.command()
@commands.is_owner()
async def poll(ctx, *, question: str):
    embed = discord.Embed(title="poll", description=question)
    msg = await ctx.send(embed=embed)
    await msg.add_reaction("👍")
    await msg.add_reaction("👎")

@bot.command()
@commands.is_owner()
async def announce(ctx, channel: discord.TextChannel, *, message: str):
    await channel.send(message)

@bot.command()
@commands.is_owner()
@commands.has_permissions(administrator=True)
async def prune(ctx, days: int):
    pruned = await ctx.guild.prune_members(days=days, compute_prune_count=False)
    await ctx.send(f"pruned {pruned} members")

@bot.command()
@commands.is_owner()
@commands.has_permissions(move_members=True)
async def voicekick(ctx, member: discord.Member):
    if member.voice:
        await member.move_to(None)
        await ctx.send(f"kicked {member.mention} from voice")

bot.run("MTQzNDEwNjY3OTU3NzkzNjAyMg.GcTG6X.CHuVf_nCw97PR_J4k4t-PgRN2lIgm2KKea63QA")
