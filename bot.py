import discord
from discord.ext import commands, tasks
import os
import itertools
from keep_alive import keep_alive

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

status_rotation = itertools.cycle([
    "Type /ai to chat!",
    "📱 Monitoring active servers",
    "👀 Watching over the server"
])

@bot.event
async def on_ready():
    print(f"🤖 Connected successfully as: {bot.user.name}")
    
    # Make sure background status rotation loops are armed
    if not change_status.is_running():
        change_status.start()
        
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

@tasks.loop(seconds=10)
async def change_status():
    await bot.change_presence(activity=discord.Game(next(status_rotation)))

async def load_cogs():
    # Automatically loop through and mount all files inside your cogs directory
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                print(f"📦 Successfully mounted cog module: {filename}")
            except Exception as e:
                print(f"❌ Failed loading cog module {filename}: {e}")

async def main():
    keep_alive()
    await load_cogs()
    # Pulls token environment safely from your Render environment variables dashboard
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
