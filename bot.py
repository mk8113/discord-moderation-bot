# ============================================================
#  Discord Bot — Moderation + Games + AI
#  Author : mk8113
#  Stack  : Python 3.10+ / discord.py / openai
# ============================================================

import discord
from discord.ext import commands
from openai import AsyncOpenAI
import random
import asyncio
import json
import os
import config

# ── Intents ─────────────────────────────────────────────────
intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix=config.PREFIX, intents=intents)
client_ai = AsyncOpenAI(api_key=config.OPENAI_API_KEY)

# ── Warn storage ─────────────────────────────────────────────
WARNS_FILE = "warns.json"

def load_warns():
    if not os.path.exists(WARNS_FILE):
        return {}
    with open(WARNS_FILE, "r") as f:
        return json.load(f)

def save_warns(data):
    with open(WARNS_FILE, "w") as f:
        json.dump(data, f, indent=4)

# ── Log utility ──────────────────────────────────────────────
async def log_action(guild, message, color=discord.Color.orange()):
    log_channel = discord.utils.get(guild.text_channels, name="logs")
    if log_channel:
        embed = discord.Embed(description=message, color=color)
        await log_channel.send(embed=embed)

# ── Active guessing games ────────────────────────────────────
active_games = {}

# ── Trivia questions ─────────────────────────────────────────
QUESTIONS = [
    {"question": "What is the capital of Belgium?",          "answer": "brussels",  "hint": "Also the capital of the EU 🇪🇺"},
    {"question": "What is 15 x 15?",                         "answer": "225",       "hint": "Between 200 and 250"},
    {"question": "What language does discord.py use?",       "answer": "python",    "hint": "It's a snake 🐍"},
    {"question": "What year was Discord created?",           "answer": "2015",      "hint": "Early 2010s"},
    {"question": "How many layers does the OSI model have?", "answer": "7",         "hint": "Between 5 and 10"},
    {"question": "What is the secure web protocol?",         "answer": "https",     "hint": "HTTP + S"},
    {"question": "What color is the sky?",                   "answer": "blue",      "hint": "Primary color 🔵"},
]

# ════════════════════════════════════════════════════════════
#  EVENTS
# ════════════════════════════════════════════════════════════

@bot.event
async def on_ready():
    print(f"✅ Bot connected as {bot.user} (ID: {bot.user.id})")
    await bot.change_presence(activity=discord.Game(name="!help for commands"))

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.text_channels, name="general")
    if not channel:
        channel = member.guild.system_channel
    if channel:
        embed = discord.Embed(
            title=f"👋 Welcome {member.name}!",
            description=f"Glad to have you here {member.mention}!\nType `!help` to see available commands.",
            color=discord.Color.green()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        await channel.send(embed=embed)
    await log_action(member.guild, f"📥 **{member}** joined the server.", discord.Color.green())

@bot.event
async def on_member_remove(member):
    await log_action(member.guild, f"📤 **{member}** left the server.", discord.Color.red())

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("❌ You don't have permission to use this command.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Member not found.")
    elif isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument. Use `!help {ctx.command}` for usage.")

# ════════════════════════════════════════════════════════════
#  MODERATION
# ════════════════════════════════════════════════════════════

@bot.command(help="Warn a member | Usage: !warn @member reason")
@commands.has_permissions(manage_messages=True)
async def warn(ctx, member: discord.Member, *, reason="No reason provided"):
    warns = load_warns()
    user_id = str(member.id)
    if user_id not in warns:
        warns[user_id] = []
    warns[user_id].append({
        "reason": reason,
        "by": str(ctx.author),
        "date": str(discord.utils.utcnow())
    })
    save_warns(warns)
    total = len(warns[user_id])
    embed = discord.Embed(
        title="⚠️ Warning",
        description=f"{member.mention} has been warned.\n**Reason:** {reason}\n**Total warns:** {total}",
        color=discord.Color.yellow()
    )
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"⚠️ **Warn**: {member} by {ctx.author} — {reason}")

@bot.command(help="Show warns of a member | Usage: !warns @member")
@commands.has_permissions(manage_messages=True)
async def warns(ctx, member: discord.Member):
    data = load_warns()
    user_id = str(member.id)
    if user_id not in data or len(data[user_id]) == 0:
        await ctx.send(f"✅ {member.mention} has no warns.")
        return
    liste = "\n".join([
        f"**{i+1}.** {w['reason']} — by {w['by']}"
        for i, w in enumerate(data[user_id])
    ])
    embed = discord.Embed(
        title=f"⚠️ Warns for {member.name}",
        description=liste,
        color=discord.Color.yellow()
    )
    await ctx.send(embed=embed)

@bot.command(help="Clear warns of a member | Usage: !clearwarns @member")
@commands.has_permissions(administrator=True)
async def clearwarns(ctx, member: discord.Member):
    data = load_warns()
    data[str(member.id)] = []
    save_warns(data)
    await ctx.send(f"✅ Warns cleared for {member.mention}.")
    await log_action(ctx.guild, f"🗑️ **Warns cleared**: {member} by {ctx.author}")

@bot.command(help="Mute a member | Usage: !mute @member reason")
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, *, reason="No reason provided"):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False, speak=False)
    await member.add_roles(muted_role)
    embed = discord.Embed(
        title="🔇 Member muted",
        description=f"{member.mention} has been muted.\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"🔇 **Mute**: {member} by {ctx.author} — {reason}")

@bot.command(help="Unmute a member | Usage: !unmute @member")
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role and muted_role in member.roles:
        await member.remove_roles(muted_role)
        await ctx.send(f"✅ {member.mention} has been unmuted.")
        await log_action(ctx.guild, f"🔊 **Unmute**: {member} by {ctx.author}")
    else:
        await ctx.send(f"❌ {member.mention} is not muted.")

@bot.command(help="Kick a member | Usage: !kick @member reason")
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    embed = discord.Embed(
        title="👢 Member kicked",
        description=f"{member.mention} has been kicked.\n**Reason:** {reason}",
        color=discord.Color.red()
    )
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"👢 **Kick**: {member} by {ctx.author} — {reason}")

@bot.command(help="Ban a member | Usage: !ban @member reason")
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    embed = discord.Embed(
        title="🔨 Member banned",
        description=f"{member.mention} has been banned.\n**Reason:** {reason}",
        color=discord.Color.dark_red()
    )
    await ctx.send(embed=embed)
    await log_action(ctx.guild, f"🔨 **Ban**: {member} by {ctx.author} — {reason}")

@bot.command(help="Unban a member | Usage: !unban name#0000")
@commands.has_permissions(ban_members=True)
async def unban(ctx, *, member):
    banned_users = [entry async for entry in ctx.guild.bans()]
    for ban_entry in banned_users:
        user = ban_entry.user
        if str(user) == member:
            await ctx.guild.unban(user)
            await ctx.send(f"✅ {user.mention} has been unbanned.")
            await log_action(ctx.guild, f"✅ **Unban**: {user} by {ctx.author}")
            return
    await ctx.send(f"❌ User {member} not found in ban list.")

@bot.command(help="Open a support ticket | Usage: !ticket")
async def ticket(ctx):
    guild = ctx.guild
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
    }
    for role in guild.roles:
        if role.permissions.administrator:
            overwrites[role] = discord.PermissionOverwrite(read_messages=True)
    channel = await guild.create_text_channel(
        f"ticket-{ctx.author.name}",
        overwrites=overwrites
    )
    embed = discord.Embed(
        title="🎫 Ticket opened",
        description=f"Hello {ctx.author.mention}!\nDescribe your issue and a staff member will assist you.\n\nType `!closeticket` to close this ticket.",
        color=discord.Color.blue()
    )
    await channel.send(embed=embed)
    await ctx.send(f"✅ Ticket created: {channel.mention}")
    await log_action(ctx.guild, f"🎫 **Ticket opened** by {ctx.author}")

@bot.command(help="Close the current ticket | Usage: !closeticket")
async def closeticket(ctx):
    if "ticket-" in ctx.channel.name:
        await ctx.send("🔒 Ticket closing in 5 seconds...")
        await asyncio.sleep(5)
        await ctx.channel.delete()
        await log_action(ctx.guild, f"🔒 **Ticket closed**: #{ctx.channel.name}")
    else:
        await ctx.send("❌ This command only works inside a ticket channel.")

@bot.command(help="Delete messages | Usage: !clear 10")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 5):
    if amount > 100:
        await ctx.send("❌ Maximum 100 messages at a time.")
        return
    deleted = await ctx.channel.purge(limit=amount + 1)
    msg = await ctx.send(f"🗑️ {len(deleted) - 1} messages deleted.")
    await asyncio.sleep(3)
    await msg.delete()
    await log_action(ctx.guild, f"🗑️ **Clear**: {len(deleted)-1} messages in #{ctx.channel.name} by {ctx.author}")

# ════════════════════════════════════════════════════════════
#  AI (OpenAI)
# ════════════════════════════════════════════════════════════

@bot.command(help="Ask the AI a question | Usage: !ai your question")
async def ai(ctx, *, question):
    async with ctx.typing():
        try:
            response = await client_ai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a friendly assistant on a Discord server. "
                            "Reply in a short, casual, and helpful way. Max 200 words."
                        )
                    },
                    {"role": "user", "content": question}
                ],
                max_tokens=300
            )
            answer = response.choices[0].message.content
            embed = discord.Embed(
                title="🤖 AI Response",
                description=answer,
                color=discord.Color.blurple()
            )
            embed.set_footer(text=f"Question by {ctx.author.name}")
            await ctx.send(embed=embed)
        except Exception as e:
            await ctx.send(f"❌ AI error: {e}")

# ════════════════════════════════════════════════════════════
#  GAMES
# ════════════════════════════════════════════════════════════

@bot.command(name="rps", help="Rock Paper Scissors | Usage: !rps rock")
async def rock_paper_scissors(ctx, choice: str):
    choice = choice.lower()
    options = ["rock", "paper", "scissors"]
    emojis = {"rock": "🪨", "paper": "📄", "scissors": "✂️"}

    if choice not in options:
        await ctx.send("❌ Choose between: `rock`, `paper` or `scissors`")
        return

    bot_choice = random.choice(options)

    if choice == bot_choice:
        result = "🤝 It's a tie!"
        color = discord.Color.yellow()
    elif (
        (choice == "rock"     and bot_choice == "scissors") or
        (choice == "paper"    and bot_choice == "rock")     or
        (choice == "scissors" and bot_choice == "paper")
    ):
        result = "🎉 You win!"
        color = discord.Color.green()
    else:
        result = "😈 I win!"
        color = discord.Color.red()

    embed = discord.Embed(title="Rock Paper Scissors", color=color)
    embed.add_field(name="Your choice", value=f"{emojis[choice]} {choice.capitalize()}", inline=True)
    embed.add_field(name="My choice",   value=f"{emojis[bot_choice]} {bot_choice.capitalize()}", inline=True)
    embed.add_field(name="Result",      value=result, inline=False)
    await ctx.send(embed=embed)

@bot.command(help="Number guessing game (1-100) | Usage: !guess")
async def guess(ctx):
    if ctx.channel.id in active_games:
        await ctx.send("❌ A game is already running in this channel!")
        return

    secret = random.randint(1, 100)
    active_games[ctx.channel.id] = secret
    max_tries = 7
    tries = 0

    embed = discord.Embed(
        title="🎮 Guessing Game!",
        description=f"I picked a number between **1 and 100**.\nYou have **{max_tries} attempts**. Go!",
        color=discord.Color.purple()
    )
    await ctx.send(embed=embed)

    def check(m):
        return m.channel == ctx.channel and m.content.isdigit() and not m.author.bot

    while tries < max_tries:
        try:
            msg = await bot.wait_for("message", check=check, timeout=30.0)
            number = int(msg.content)
            tries += 1
            remaining = max_tries - tries

            if number < secret:
                await ctx.send(f"⬆️ Higher! ({remaining} attempts left)")
            elif number > secret:
                await ctx.send(f"⬇️ Lower! ({remaining} attempts left)")
            else:
                embed = discord.Embed(
                    title="🎉 You got it!",
                    description=f"Well done {msg.author.mention}! It was **{secret}** in {tries} attempt(s)!",
                    color=discord.Color.green()
                )
                await ctx.send(embed=embed)
                del active_games[ctx.channel.id]
                return

        except asyncio.TimeoutError:
            await ctx.send(f"⏰ Time's up! It was **{secret}**.")
            del active_games[ctx.channel.id]
            return

    await ctx.send(f"💀 Out of attempts! It was **{secret}**.")
    del active_games[ctx.channel.id]

@bot.command(help="Trivia quiz | Usage: !trivia")
async def trivia(ctx):
    q = random.choice(QUESTIONS)
    embed = discord.Embed(
        title="🧠 Trivia!",
        description=q["question"],
        color=discord.Color.gold()
    )
    embed.set_footer(text="⏰ 20 seconds to answer!")
    await ctx.send(embed=embed)

    def check(m):
        return m.channel == ctx.channel and not m.author.bot

    try:
        msg = await bot.wait_for("message", check=check, timeout=20.0)
        if msg.content.lower().strip() == q["answer"]:
            await ctx.send(f"✅ Correct {msg.author.mention}! 🎉")
        else:
            embed = discord.Embed(
                title="❌ Wrong answer",
                description=f"💡 Hint: {q['hint']}\n✅ Answer: **{q['answer'].capitalize()}**",
                color=discord.Color.red()
            )
            await ctx.send(embed=embed)
    except asyncio.TimeoutError:
        await ctx.send(f"⏰ Time's up! The answer was: **{q['answer'].capitalize()}**")

@bot.command(help="Roll a dice | Usage: !dice 6")
async def dice(ctx, faces: int = 6):
    if faces < 2 or faces > 100:
        await ctx.send("❌ The dice must have between 2 and 100 faces.")
        return
    result = random.randint(1, faces)
    await ctx.send(f"🎲 You rolled a {faces}-sided dice... **{result}**!")

@bot.command(help="Heads or tails | Usage: !coin")
async def coin(ctx):
    result = random.choice(["🪙 Heads!", "🪙 Tails!"])
    await ctx.send(result)

# ════════════════════════════════════════════════════════════
#  RUN
# ════════════════════════════════════════════════════════════

bot.run(config.TOKEN)
