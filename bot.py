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

# --- FIXED INDENTATION LOGIC ---
@bot.event
async def setup_hook():
    logger.info("📂 Scanning and mounting cog extensions...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"
            try:
                await bot.load_extension(cog_name)
                logger.info(f"📦 Successfully mounted cog module: {filename}")
            except Exception as e:
                logger.error(f"❌ CRITICAL LOAD FAILURE inside {filename}: {e}")

@bot.event
async def on_ready():
    logger.info(f"🤖 Connected successfully as: {bot.user.name}")
    
    if not change_status.is_running():
        change_status.start()
        
    try:
        logger.info("🔄 Syncing slash command tree with Discord globally...")
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
    clean_output = '\n'.join(full_logs.split('\n')[-15:])
    try:
        await ctx.author.send(f"📋 **Logs:**\n```text\n{clean_output}\n```")
        await ctx.message.add_reaction("📨")
    except:
        await ctx.send("❌ Cannot DM logs.")

@bot.command(name="sync")
async def manual_sync(ctx):
    if ctx.author.name not in ["lyzy01", "kimmendez01"]:
        return await ctx.send("❌ Access Denied.")
    try:
        synced = await bot.tree.sync()
        await ctx.send(f"✅ Manually forced synchronization of {len(synced)} slash commands!")
    except Exception as e:
        await ctx.send(f"❌ Force sync failed: {e}")

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status_rotation)))

async def main():
    keep_alive()
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
