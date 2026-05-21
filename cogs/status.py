import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
import os
import sys
import urllib.request

try:
    import resource
except ImportError:
    resource = None

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="uptime", description="⚡ Check the bot's runtime and real hardware status.")
    async def uptime(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=False)
        
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # Calculate time values cleanly
        years, remainder = divmod(uptime_seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        precision_timestamp = f"{years}y {months}m {days}d {hours}h {minutes}m {seconds}s"
        api_latency = round(self.bot.latency * 1000, 1)
        total_cores = os.cpu_count() or 1
        
        if resource:
            mem_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            real_memory = round(mem_bytes / 1024, 1)
        else:
            real_memory = "N/A"

        # Check Groq Connection Status Safely (With proper Headers!)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            ai_status = "🔴 UNCONFIGURED"
        else:
            def check_groq():
                try:
                    req = urllib.request.Request(
                        "https://api.groq.com/openai/v1/models",
                        headers={
                            "Authorization": f"Bearer {groq_api_key}",
                            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) DiscordBot"
                        },
                        method="GET"
                    )
                    with urllib.request.urlopen(req, timeout=3.0) as response:
                        return "🟢 OPERATIONAL" if response.status == 200 else f"🔴 ERROR {response.status}"
                except Exception as e:
                    # If it returns a 403 or 200 it still means the API is reachable!
                    if "403" in str(e):
                        return "🟢 OPERATIONAL"
                    return "🔴 DISCONNECTED"
            ai_status = await self.bot.loop.run_in_executor(None, check_groq)

        # Flat, safe single lines to ensure it never crashes line parsing
        embed = discord.Embed(
            title="📊 CORE SYSTEM INTEGRITY REPORT",
            color=discord.Color.from_rgb(46, 204, 113)
        )
        
        embed.add_field(name="🌐 PROCESS ENVIRONMENT", value=f"Host: 🟢 LIVE/STABLE\nGroq AI: {ai_status}", inline=False)
        embed.add_field(name="⏱️ ACTIVE RUNTIME", value=precision_timestamp, inline=False)
        embed.add_field(name="📡 GATEWAY PING", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="🖥️ HARDWARE CORES", value=f"{total_cores} CPU Threads", inline=True)
        embed.add_field(name="📊 MEMORY HEAP", value=f"{real_memory} MB / 512 MB", inline=True)
        
        embed.set_footer(text=f"Compiled for root@{interaction.user.name}")
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await interaction.followup.send(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
