import discord
from discord.ext import commands
import asyncio
import os

intents = discord.Intents.all()
bot = commands.Bot(command_prefix='.', intents=intents)

# ---------------- CONFIG ----------------
antinuke_enabled = {}
punishment_type = {}
extra_owner = {}
whitelist = {}
automod_enabled = {}
welcome_channels = {}

# ---------------- EVENTS ----------------
@bot.event
async def on_ready():
    print(f"{bot.user} is online.")

@bot.event
async def on_member_join(member):
    guild_id = member.guild.id
    if guild_id in welcome_channels:
        channel = bot.get_channel(welcome_channels[guild_id])
        if channel:
            await channel.send(f"Welcome {member.mention} to {member.guild.name}!")

# ---------------- ANTINUKE ----------------
@bot.command()
async def antinuke(ctx, action=None):
    gid = ctx.guild.id
    if action == "enable":
        antinuke_enabled[gid] = True
        await ctx.send("✅ AntiNuke enabled")
    elif action == "disable":
        antinuke_enabled[gid] = False
        await ctx.send("❌ AntiNuke disabled")
    elif action == "show":
        status = antinuke_enabled.get(gid, False)
        await ctx.send(f"AntiNuke status: {status}")

# ---------------- PUNISHMENT ----------------
@bot.command()
async def punishment(ctx, ptype=None):
    gid = ctx.guild.id
    if ptype in ['kick','ban','quarantine']:
        punishment_type[gid] = ptype
        await ctx.send(f"Punishment set to {ptype}")

# ---------------- EXTRA OWNER ----------------
@bot.command()
async def extraowner(ctx, action=None, member: discord.Member=None):
    gid = ctx.guild.id
    if action == 'add' and member:
        extra_owner[gid] = member.id
        await ctx.send(f"Added {member}")
    elif action == 'show':
        await ctx.send(str(extra_owner.get(gid,'None')))
    elif action == 'reset':
        extra_owner.pop(gid,None)
        await ctx.send('Reset done')

# ---------------- WHITELIST ----------------
@bot.command()
async def whitelist_add(ctx, member: discord.Member):
    gid = ctx.guild.id
    whitelist.setdefault(gid,[]).append(member.id)
    await ctx.send('Whitelisted')

@bot.command()
async def unwhitelist(ctx, member: discord.Member):
    gid = ctx.guild.id
    if member.id in whitelist.get(gid,[]):
        whitelist[gid].remove(member.id)
    await ctx.send('Removed')

# ---------------- AUTOMOD ----------------
@bot.command()
async def automod(ctx, action=None):
    gid = ctx.guild.id
    if action=='enable':
        automod_enabled[gid]=True
        await ctx.send('Automod enabled')
    elif action=='disable':
        automod_enabled[gid]=False
        await ctx.send('Automod disabled')

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    banned_words=['spam','badword','scam']
    if automod_enabled.get(message.guild.id,False):
        for word in banned_words:
            if word in message.content.lower():
                await message.delete()
                await message.channel.send(f'{message.author.mention} blocked by automod')
                return

    await bot.process_commands(message)

# ---------------- WELCOME ----------------
@bot.command()
async def welcome(ctx, action=None):
    gid = ctx.guild.id
    if action=='setup':
        welcome_channels[gid]=ctx.channel.id
        await ctx.send('Welcome configured')
    elif action=='config':
        await ctx.send(str(welcome_channels.get(gid,'Not set')))
    elif action=='reset':
        welcome_channels.pop(gid,None)
        await ctx.send('Reset')

# ---------------- RUN ----------------
bot.run(os.getenv("TOKEN"))
