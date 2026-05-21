import discord
from discord.ext import commands
from discord import app_commands

class ServerAudit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server-audit", description="Performs a complete security and health scan of the server.")
    @app_commands.default_permissions(manage_guild=True)
    async def server_audit(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Security authorization check
        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != guild.owner_id:
            await interaction.response.send_message("
http://googleusercontent.com/immersive_entry_chip/0

---

### What to do now:
1. Save and **Commit changes** to your `cogs/audit.py` file on GitHub.
2. Go to Render, perform a **Manual Deploy -> Clear Build Cache & Deploy** to ensure it drops the old broken files completely.
3. Keep an eye on the Render logs. You should see `📦 Successfully mounted cog module: audit.py` pop up with no errors!
