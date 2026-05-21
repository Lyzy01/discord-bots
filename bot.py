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

# 🚨 EMERGENCY TEXT PASS-THROUGH COMMAND (FIXED STRING FORMATTING) 🚨
@bot.command(name="check")
async def emergency_check(ctx):
    if ctx.author.name not in ["lyzy01", "kimmendez01"]:
        return

    full_logs = log_capture_buffer.getvalue()
    recent_lines = full_logs.split('\n')[-15:]
    clean_output = '\n'.join(recent_lines)
    
    try:
        await ctx.author.send(f"📋 **Emergency Diagnostics:**\n```text\n{clean_output}\n```")
        await ctx.message.add_reaction("📨")
    except Exception as e:
        # Keep everything on a single safe text string line to avoid Python parser crashes
        await ctx.send(f"⚠️ Cannot DM logs. Snippet: 
http://googleusercontent.com/immersive_entry_chip/0

---

### 🚀 Save and Verify

1. Update **`bot.py`** with this version on GitHub and commit changes.
2. Watch your Render dashboard. The logs will read `==> Build successful 🎉` and then run smoothly without hitting the syntax error.
3. Once Render shows your deployment as active, go to Discord and run your slash menu or type **`!sync`** if your client needs an immediate update. Your `/uptime` command will finally show up!
