import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
import os
import sys
import httpx  # Used for the live Groq API status handshake

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

        # 🟢/🔴 LIVE API HEALTH CHECK (Groq Handshake)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            ai_status = "🔴 UNCONFIGURED"
        else:
            try:
                # Send a lightweight test ping to Groq's official endpoint
                async with httpx.AsyncClient() as client:
                    response = await client.get("https://api.groq.com/openai/v1/models", headers={
                        "Authorization": f"Bearer {groq_api_key}"
                    }, timeout=3.0)
                
                if response.status_code == 200:
                    ai_status = "🟢 OPERATIONAL"
                else:
                    ai_status = f"🔴 ERROR {response.status_code}"
            except Exception:
                ai_status = "🔴 TIMEOUT / DOWN"

        # 🎨 Advanced Clean Dashboard Embed
        embed = discord.Embed(
            title="📊 CORE SYSTEM INTEGRITY REPORT",
            color=discord.Color.from_rgb(46, 204, 113) # Matrix Emerald Green
        )
        
        # Your status indicator highlights added right at the top!
        embed.add_field(
            name="🌐 INSTANCE DEPLOYMENT STATUS",
            value=f">>> 🟢 **Render Host Process:** `LIVE / STABLE`\n{ai_status} **Groq AI Framework Pipeline**",
            inline=False
        )
        
        embed.add_field(
            name="⏱️ TIME SINCE LAST REBOOT", 
            value=f"
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2
http://googleusercontent.com/immersive_entry_chip/3
4. Give your client a quick reboot (`Ctrl + R`).

Now when you trigger `/uptime`, you'll get a beautifully formatted, emerald-themed breakdown showing the exact health circles of your hosting infrastructure and your active AI connection!
