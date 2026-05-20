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
    
    # --- SAFE EXTENSION MOUNTING ---
    # We load cogs right here when the bot client is fully operational
    print("📂 Scanning and mounting cog extensions...")
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py") and not filename.startswith("__"):
            cog_name = f"cogs.{filename[:-3]}"
            # Prevent duplicate load errors on reconnects
            if cog_name not in bot.extensions:
                try:
                    await bot.load_extension(cog_name)
                    print(f"📦 Successfully mounted cog module: {filename}")
                except Exception as e:
                    print(f"❌ Failed loading cog module {filename}: {e}")
    
    # Make sure background status rotation loops are armed
    if not change_status.is_running():
        change_status.start()
        
    # Sync the commands AFTER all cogs are successfully mounted
    try:
        print("🔄 Syncing slash command tree with Discord...")
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# Manual prefix command to force sync if Discord client cache freezes
@bot.command(name="sync")
async def manual_sync(ctx):
    # Only allow the bot owner or staff to sync manually
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    is_staff = any(any(k in role.name.lower() for k in admin_keywords) for role in ctx.author.roles) or ctx.author.name == "kimmendez01"
    
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
    # Start the bot directly; loading and syncing are now handled cleanly on boot inside on_ready
    await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
