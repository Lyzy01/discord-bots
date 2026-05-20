import discord
from discord.ext import commands
import os
from keep_alive import keep_alive

# Initialize bot with all necessary intents
intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"🤖 Connected successfully as: {bot.user.name}")
    print(f"🆔 Bot ID: {bot.user.id}")
    
    # Sync slash commands globally with Discord
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")
        
    await bot.change_presence(activity=discord.Game(name="Watching over the server 👀"))

async def load_cogs():
    # Loading all 5 cogs cleanly
    for cog in ['general', 'moderation', 'fun', 'music', 'ai']:
        try:
            await bot.load_extension(f'cogs.{cog}')
            print(f"📁 Cog Loaded: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog [{cog}]: {e}")

async def main():
    async with bot:
        await load_cogs()
        # Reads token from Render Environment Variables
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    keep_alive()  # Starts Flask web server for Render
    import asyncio
    asyncio.run(main())
