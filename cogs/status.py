import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
import os
import sys
import urllib.request  # Native Python library - will never cause an installation crash!

try:
    import resource
except ImportError:
    resource = None

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="uptime", description="📊 Pull a comprehensive real-time system metrics and environment diagnostics report.")
    async def uptime(self, interaction: discord.Interaction):
        # Defer immediately to give us time to check the external Groq API status
        await interaction.response.defer(ephemeral=False)
        
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # ⏱️ Precise Runtime Calculations
        years, remainder = divmod(uptime_seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        precision_timestamp = f"{years}y {months}m {days}d {hours}h {minutes}m {seconds}s"
        
        # 📡 Live Network Gateway Metrics
        api_latency = round(self.bot.latency * 1000, 1)
        
        # 🖥️ Real Resource Polling
        total_cores = os.cpu_count() or 1
        if resource:
            mem_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            real_memory = round(mem_bytes / 1024, 1)
        else:
            real_memory = "N/A"

        # 📊 Real Live Scope Statistics
        total_guilds = len(self.bot.guilds)
        total_users = sum(guild.member_count for guild in self.bot.guilds if guild.member_count)
        total_commands = len(self.bot.tree.get_commands())

        # ⚙️ Python Environment Data
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"

        # 🟢/🔴 LIVE API HEALTH CHECK (Native Handshake)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            ai_status = "🔴 UNCONFIGURED"
        else:
            # Run the handshake inside an executor thread so it doesn't freeze the bot
            def check_groq():
                try:
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/models",
                        headers={"Authorization": f"Bearer {groq_api_key}"},
                        method="GET"
                    )
                    with urllib.request.urlopen(req, timeout=3.0) as response:
                        return "🟢 OPERATIONAL" if response.status == 200 else f"🔴 ERROR {response.status}"
                except Exception:
                    return "🔴 TIMEOUT / DOWN"

            ai_status = await self.bot.loop.run_in_executor(None, check_groq)

        # 🎨 Advanced Clean Dashboard Embed
        embed = discord.Embed(
            title="📊 CORE SYSTEM INTEGRITY REPORT",
            color=discord.Color.from_rgb(46, 204, 113) # Matrix Emerald Green
        )
        
        embed.add_field(
            name="🌐 INSTANCE DEPLOYMENT STATUS",
            value=f"> 🟢 **Render Host Process:** `LIVE / STABLE`\n> {ai_status} **Groq AI Framework Pipeline**",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ TIME SINCE LAST REBOOT", 
            value=f"
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2
http://googleusercontent.com/immersive_entry_chip/3

Do a quick app restart (`Ctrl + R`), and your shiny new metrics dashboard will be back in place permanently!
