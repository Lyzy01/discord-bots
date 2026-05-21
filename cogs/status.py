import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
import os

try:
    import resource
except ImportError:
    resource = None

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.start_time = time.time()

    @app_commands.command(name="uptime", description="⚡ Display real live system metrics and engine runtime.")
    async def uptime(self, interaction: discord.Interaction):
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # Time Calculations
        years, remainder = divmod(uptime_seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        precision_timestamp = f"{years}y {months}m {days}d {hours}h {minutes}m {seconds}s"
        
        # Hardware Polling
        api_latency = round(self.bot.latency * 1000, 1)
        total_cores = os.cpu_count() or 1
        
        if resource:
            mem_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            real_memory = round(mem_bytes / 1024, 1)
        else:
            real_memory = "N/A"

        # Safe, flat single-line strings to avoid wrap syntax crashes
        embed = discord.Embed(
            title="⚡ REAL-TIME ENGINE DIAGNOSTICS",
            color=discord.Color.from_rgb(0, 240, 255)
        )
        
        embed.add_field(name="⏱️ RUNTIME STATUS", value=precision_timestamp, inline=False)
        embed.add_field(name="🖥️ HARDWARE ALLOCATION", value=f"CPU Threads: {total_cores} active", inline=False)
        embed.add_field(name="📡 LATENCY PING", value=f"{api_latency}ms", inline=True)
        embed.add_field(name="📊 INSTANCE MEMORY", value=f"{real_memory} MB / 512 MB", inline=True)
        
        embed.set_footer(text=f"Polled by root@{interaction.user.name}")
        embed.timestamp = datetime.datetime.now(datetime.timezone.utc)
        
        await interaction.response.send_message(embed=embed)

async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
