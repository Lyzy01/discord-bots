import discord
from discord.ext import commands, tasks
import os
import itertools
import logging
import io
from keep_alive import keep_alive

# Setup logging capture for the !check command
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
async def setup_hook():
    logger.info("📂 Starting absolute directory scan for cogs...")
    
    # Force the path to be absolute to prevent Render environment confusion
    cogs_dir = os.path.abspath("./cogs")
    
    if not os.path.exists(cogs_dir):
        logger.critical(f"❌ CRITICAL: The directory {cogs_dir} was not found!")
        return

    # Get a clean list of files and filter out system files
    files = [f for f in os.listdir(cogs_dir) if f.endswith(".py") and not f.startswith("__")]
    logger.info(f"📋 Found {len(files)} potential target files in cogs folder: {files}")

    for filename in files:
        cog_name = f"cogs.{filename[:-3]}"
        try:
            logger.info(f"🔄 Attempting to mount module: {filename}")
            await bot.load_extension(cog_name)
            logger.info(f"📦 Successfully mounted cog module: {filename}")
        except Exception as e:
            logger.error(f"❌ FAILED TO MOUNT {filename}: {e}")

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

# 🚨 DIAGNOSTIC LOG CHECK COMMAND 🚨
@bot.command(name="check")
async def emergency_check(ctx):
    if ctx.author.name not in ["lyzy01", "kimmendez01"]:
        return
    full_logs = log_capture_buffer.getvalue()
    # Grabs the last 30 lines to make sure we don't miss anything
    clean_output = '\n'.join(full_logs.split('\n')[-30:])
    try:
        await ctx.author.send(f"📋 **System Diagnostic Logs:**\n```text\n{clean_output}\n```")
        await ctx.message.add_reaction("📨")
    except:
        await ctx.send("❌ Cannot DM logs. Please open your DMs for this bot.")

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
    if bot.is_ready():
        try:
            await bot.change_presence(activity=discord.Game(next(status_rotation)))
        except:
            pass

async def main():
    # Keep alive runs instantly to satisfy Render's port binder
    keep_alive()
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        logger.critical("❌ DISCORD_TOKEN environment variable is missing!")
        return
    await bot.start(token)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
