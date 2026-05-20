import discord
from discord.ext import commands, tasks
import os
import itertools
from keep_alive import keep_alive

intents = discord.Intents.all()
bot = commands.Bot(command_prefix="!", intents=intents)

# Creating a cycle loop for changing statuses automatically
status_rotation = itertools.cycle([
    "💬 Type /ai to chat!",
    "🌐 Monitoring active servers",
    "👀 Watching over the server"
])

@bot.event
@bot.event
async def on_ready():
    print(f"🤖 Connected successfully as: {bot.user.name}")
    
    # Registering all permanent interactive layouts
    from cogs.tickets import ReportButtonView, AppealButtonView, CloseTicketView
    bot.add_view(ReportButtonView())
    bot.add_view(AppealButtonView())
    bot.add_view(CloseTicketView()) # This keeps the cancel button alive forever
    print("🔘 Persistent Interface Buttons Armed Successfully!")
    
    try:
        synced = await bot.tree.sync()
        print(f"✅ Synced {len(synced)} slash commands globally!")
    except Exception as e:
        print(f"❌ Failed to sync commands: {e}")

# This task runs background loops every 10 seconds to swap statuses dynamically
@tasks.loop(seconds=10)
async def change_status():
    current_status = next(status_rotation)
    # Customize the text dynamically depending on what's active
    if "servers" in current_status:
        text = f"🌐 in {len(bot.guilds)} servers!"
    else:
        text = current_status
        
    await bot.change_presence(activity=discord.Game(name=text))

async def load_cogs():
    # Adding 'tickets' directly into the live tracking array
    for cog in ['general', 'moderation', 'fun', 'music', 'ai', 'admin', 'tickets']:
        try:
            await bot.load_extension(f'cogs.{cog}')
            print(f"📁 Cog Loaded: {cog}")
        except Exception as e:
            print(f"❌ Failed to load cog [{cog}]: {e}")

async def main():
    async with bot:
        await load_cogs()
        await bot.start(os.getenv("DISCORD_TOKEN"))

if __name__ == "__main__":
    keep_alive()
    import asyncio
    asyncio.run(main())
