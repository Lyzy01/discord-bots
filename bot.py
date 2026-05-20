import discord
from discord import app_commands
from discord.ext import commands, tasks
import os
import itertools
import logging
import io
from keep_alive import keep_alive

# --- LIVE TERMINAL CAPTURE ENGINE ---
# This captures all standard python logging prints into a memory buffer
log_capture_buffer = io.StringIO()
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(log_capture_buffer),  # Saves logs to memory for the /logs command
        logging.StreamHandler()                    # Still prints logs to your Render dashboard screen
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
    
    # --- SAFE EXTENSION MOUNTING ---
    logger.info("📂 Scanning and mounting cog extensions...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"
            if cog_name not in bot.extensions:
                try:
                    await bot.load_extension(cog_name)
                    logger.info(f"📦 Successfully mounted cog module: {filename}")
                except Exception as e:
                    logger.error(f"❌ Failed loading cog module {filename}: {e}")
    
    if not change_status.is_running():
        change_status.start()
        
    try:
        logger.info("🔄 Syncing slash command tree with Discord...")
        synced = await bot.tree.sync()
        logger.info(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        logger.error(f"❌ Failed to sync commands: {e}")

# --- SECURE DEVELOPER LOGS COMMAND ---
@bot.tree.command(name="logs", description="🔒 Private Developer Tool: Fetch recent live server boot logs and errors.")
async def send_logs(interaction: discord.Interaction):
    # Strict Developer User check using your account name
    # Checks both your current display setup name and default account identity
    if interaction.user.name != "lyzy01" and interaction.user.name != "kimmendez01":
        await interaction.response.send_message("❌ **Access Denied:** This command is securely locked to the bot owner.", ephemeral=True)
        return

    # Defer response privately so people in the channel don't see you fetching logs
    await interaction.response.defer(ephemeral=True)

    try:
        # Pull the last 1500 characters from our memory stream to avoid hitting Discord's 2000 character limit
        full_logs = log_capture_buffer.getvalue()
        recent_logs = full_logs[-1800:] if len(full_logs) > 1800 else full_logs

        if not recent_logs.strip():
            recent_logs = "System buffer active. No log entries recorded yet."

        # Open a direct message channel with you
        dm_channel = interaction.user.dm_channel or await interaction.user.create_dm()
        
        # Format beautifully inside a markdown code block
        log_message = f"📋 **Live System Logs for {bot.user.name}:**\n```text\n{recent_logs}\n```"
        await dm_channel.send(log_message)
        
        # Confirm to the slash interface that it was sent safely
        await interaction.followup.send("📨 **Logs dispatched safely!** Check your Direct Messages.", ephemeral=True)
        
    except discord.Forbidden:
        await interaction.followup.send("⚠️ **Delivery Failure:** I couldn't DM you! Please verify that your 'Allow direct messages from server members' privacy setting is turned on.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"⚠️ **Internal command anomaly:** `{e}`", ephemeral=True)

@bot.command(name="sync")
async def manual_sync(ctx):
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    is_staff = any(any(k in role.name.lower() for k in admin_keywords) for role in ctx.author.roles) or ctx.author.name in ["lyzy01", "kimmendez01"]
    
    if not is_staff:
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
