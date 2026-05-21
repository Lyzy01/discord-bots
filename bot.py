import discord
from discord.ext import commands, tasks
import os
import itertools
import logging
import io
from keep_alive import keep_alive

log_capture_buffer = io.StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(log_capture_buffer),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('DiscordBot')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

status_rotation = itertools.cycle([
    "Type /ai to chat!",
    "📱 Monitoring active servers",
    "👀 Watching over the server"
])

@bot.event
async def on_ready():
    logger.info(f"🤖 Connected successfully as: {bot.user.name}")
    
    logger.info("📂 Scanning and mounting cog extensions...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"
            if cog_name not in bot.extensions:
                try:
                    await bot.load_extension(cog_name)
                    logger.info(f"📦 Successfully mounted cog module: {filename}")
                except Exception as e:
                    logger.error(f"❌ CRITICAL LOAD FAILURE inside {filename}: {e}")
    
    if not change_status.is_running():
        change_status.start()
        
    try:
        logger.info("🔄 Syncing slash command tree with Discord...")
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        logger.error(f"❌ TREE SYNC CRASHED: {e}")

# 🚨 EMERGENCY TEXT PASS-THROUGH COMMAND 🚨
@bot.command(name="check")
async def emergency_check(ctx):
    if ctx.author.name not in ["lyzy01", "kimmendez01"]:
        return

    full_logs = log_capture_buffer.getvalue()
    # Grab the last 15 lines of errors
    recent_lines = full_logs.split('\n')[-15:]
    clean_output = '\n'.join(recent_lines)
    
    try:
        await ctx.author.send(f"📋 **Emergency Diagnostics:**\n```text\n{clean_output}\n```")
        await ctx.message.add_reaction("📨")
    except Exception as e:
        await ctx.send(f"⚠️ Cannot DM logs. Terminal output slice:\n
http://googleusercontent.com/immersive_entry_chip/0

The bot will print out or DM you the exact terminal lines showing which specific file is broken (e.g., a missing variable in `tickets.py` or a layout error somewhere else). Paste what it gives you or what your Render logs show right here, and we will clean it out instantly!
