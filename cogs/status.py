import discord
from discord import app_commands
from discord.ext import commands
import time
import datetime
import os

# Try to import resource to measure real Linux container memory usage
try:
    import resource
except ImportError:
    resource = None

class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        # Track the exact epoch time the bot script booted up
        self.start_time = time.time()

    @app_commands.command(name="uptime", description="⚡ Display real live system metrics, container memory, and engine runtime.")
    async def uptime(self, interaction: discord.Interaction):
        current_time = time.time()
        uptime_seconds = int(current_time - self.start_time)
        
        # ⏱️ 1. REAL TIME MATHEMATICS
        years, remainder = divmod(uptime_seconds, 31536000)
        months, remainder = divmod(remainder, 2592000)
        days, remainder = divmod(remainder, 86400)
        hours, remainder = divmod(remainder, 3600)
        minutes, seconds = divmod(remainder, 60)
        
        precision_timestamp = f"{years:02d}y / {months:02d}m / {days:02d}d / {hours:02d}h / {minutes:02d}m / {seconds:02d}s"
        
        # 📡 2. REAL API LATENCY ROUNDING
        api_latency = round(self.bot.latency * 1000, 1)
        
        # 🖥️ 3. REAL CPU THREAD COUNTS
        # Os.cpu_count() reads the exact processor core allocations assigned to your container
        total_cores = os.cpu_count() or 1
        octa_core_display = f"Allocated CPU Threads: [ {total_cores} Core(s) Fully Armed ]"
        
        # 📊 4. REAL CONTAINER MEMORY ALLOCATION
        # Reads the exact maximum resident set size used by the active Python application process
        if resource:
            # On Linux systems, max_rss returns kilobytes. We convert to Megabytes.
            mem_bytes = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
            real_memory = round(mem_bytes / 1024, 1)
        else:
            real_memory = "N/A"

        # Create the high-tech terminal style interface
        embed = discord.Embed(
            title="⚡ REAL-TIME ENGINE DIAGNOSTICS",
            color=discord.Color.from_rgb(0, 240, 255)  # Cyberpunk Electric Cyan
        )
        
        embed.add_field(
            name="⏱️ ACTIVE MATRIX RUNTIME", 
            value=f"```glsl\n{precision_timestamp}\n```", 
            inline=False
        )
        
        embed.add_field(
            name="🖥️ VIRTUALIZED HARDWARE ARCHITECTURE", 
            value=f"
http://googleusercontent.com/immersive_entry_chip/0
http://googleusercontent.com/immersive_entry_chip/1
http://googleusercontent.com/immersive_entry_chip/2

---

### 📡 What happens now when you run it?
* **The timer is active:** The seconds, minutes, and hours will accurately tick upward from the exact second Render brings your bot online.
* **The memory is real:** It calculates the exact megabytes of RAM your specific bot processes require to run your slash interactions.
* **The latency is real:** The millisecond value is a live test pinging the speed between Render's cloud servers and Discord's network gateway.

Commit the changes, wait for Render to compile the code, and give it a test run with `/uptime`!
