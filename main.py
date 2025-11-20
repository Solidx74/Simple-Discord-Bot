import discord
from discord.ext import commands
import logging
from dotenv import load_dotenv
import os
import asyncio
import webserver

load_dotenv()
token = os.getenv("DISCORD_TOKEN")

handler = logging.FileHandler(filename='discord.log', encoding='utf-8', mode='w')
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix='$', intents=intents)

sec_role = "Crypto"

# ---------- EVENTS ----------
@bot.event
async def on_ready():
    print(f"{bot.user.name} is online! Systems booted, circuits croaking, and ready to serve.")

@bot.event
async def on_member_join(member):
    await member.send(f"Welcome {member.mention}, welcome to my server!")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # Bad word filter
    bad_words = ["shit", "fuck", "wtf", "piss"]
    if any(word in message.content.lower() for word in bad_words):
        await message.delete()
        await message.channel.send(f"{message.author.mention} - don't use that word again!")

    # Auto replies when RibBot is mentioned
    if bot.user.mentioned_in(message):
        content = message.content.lower()
        if any(word in content for word in ["hello", "hi", "hey"]):
            await message.channel.send(f"Hello {message.author.mention}! 👋")
        if "gm" in content:
            await message.channel.send("Good Morning! 🌞")
        if "gn" in content:
            await message.channel.send("Good Night! 🌙")

    await bot.process_commands(message)

# ---------- SIMPLE COMMANDS ----------
@bot.command()
async def hello(ctx):
    await ctx.send(f"Hello {ctx.author.mention}!")

@bot.command()
async def sup(ctx):
    await ctx.send(f"Doing great mate. How about you? {ctx.author.mention}")

@bot.command()
async def reply(ctx):
    await ctx.reply("Hei mate, RibBot will always reply to you!")

@bot.command()
async def dm(ctx, *, message):
    await ctx.author.send(message)

# ---------- ROLE COMMANDS ----------
@bot.command()
async def assign(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Random")
    if role:
        await ctx.author.add_roles(role)
        await ctx.send(f"{ctx.author.mention} has been given the role of Random!")
    else:
        await ctx.send("Role does not exist in this server.")

@bot.command()
async def remove(ctx):
    role = discord.utils.get(ctx.guild.roles, name="Random")
    if role:
        await ctx.author.remove_roles(role)
        await ctx.send(f"Random role removed from {ctx.author.mention}!")
    else:
        await ctx.send("Role does not exist in this server.")

# ---------- YES/NO ROLE COMMANDS ----------
@bot.command()
async def cuetian(ctx):
    await ctx.send(f"{ctx.author.mention}, are you currently studying in CUET? (yes/no)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

    try:
        msg = await bot.wait_for("message", timeout=30, check=check)
        if msg.content.lower() == "yes":
            role_obj = discord.utils.get(ctx.guild.roles, name="CUETian")
            if role_obj:
                await ctx.author.add_roles(role_obj)
                await ctx.send(f"Role **CUETian** assigned to you, {ctx.author.mention}! Thank you!")
            else:
                await ctx.send("CUETian role does not exist in this server.")
        else:
            await ctx.send("Enjoy chatting here mate 😄")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to reply!")

@bot.command()
async def crypto(ctx):
    await ctx.send(f"{ctx.author.mention}, are you interested in crypto? (yes/no)")

    def check(m):
        return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ["yes", "no"]

    try:
        msg = await bot.wait_for("message", timeout=30, check=check)
        if msg.content.lower() == "yes":
            role_obj = discord.utils.get(ctx.guild.roles, name="Crypto")
            if role_obj:
                await ctx.author.add_roles(role_obj)
                await ctx.send(f"Role **Crypto** assigned to you, {ctx.author.mention}! 🚀")
            else:
                await ctx.send("Crypto role does not exist in this server.")
        else:
            await ctx.send("Enjoy chatting here mate 😄")
    except asyncio.TimeoutError:
        await ctx.send("You took too long to reply!")

# ---------- SECRET COMMAND ----------
@bot.command()
@commands.has_role(sec_role)
async def secret(ctx):
    await ctx.send("Welcome to the Crypto club!")

@secret.error
async def secret_error(ctx, error):
    if isinstance(error, commands.MissingRole):
        await ctx.send(f"Sorry, {ctx.author.mention}. You do not have the permission to do that.")

# ---------- POLL ----------
@bot.command()
async def poll(ctx, *, question):
    embed = discord.Embed(title="New Poll", description=question, color=0x00ffcc)
    poll_message = await ctx.send(embed=embed)
    await poll_message.add_reaction("👍")
    await poll_message.add_reaction("👎")

# ---------- USER & SERVER INFO ----------
@bot.command()
async def userinfo(ctx, member: discord.Member = None):
    member = member or ctx.author
    embed = discord.Embed(title=f"User Info - {member}", color=0x00ffcc)
    embed.add_field(name="ID", value=member.id, inline=False)
    embed.add_field(name="Account Created", value=member.created_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Joined Server", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
    embed.add_field(name="Roles", value=", ".join([r.name for r in member.roles if r.name != "@everyone"]))
    embed.set_thumbnail(url=member.display_avatar.url)
    await ctx.send(embed=embed)

@bot.command()
async def serverinfo(ctx):
    guild = ctx.guild
    embed = discord.Embed(title="Server Information", color=0x3498db)
    embed.add_field(name="Server Name", value=guild.name)
    embed.add_field(name="Owner", value=str(guild.owner))
    embed.add_field(name="Members", value=guild.member_count)
    embed.add_field(name="Roles", value=len(guild.roles))
    embed.add_field(name="Created On", value=guild.created_at.strftime("%Y-%m-%d"))
    embed.set_thumbnail(url=guild.icon.url)
    await ctx.send(embed=embed)




# ---------- RUN BOT ----------
webserver.keep_alive()
bot.run(token, log_handler=handler, log_level=logging.DEBUG)
