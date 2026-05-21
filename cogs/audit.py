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
        
        # Hard fail-safe check: Require user to have Manage Guild OR be the exact Server Owner
        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != guild.owner_id:
            await interaction.response.send_message(
                "
http://googleusercontent.com/immersive_entry_chip/0

---

### What to do next:
1. Save/Commit this new version of `audit.py` on GitHub.
2. Render will see the update and start deploying it automatically.
3. Once the Render logs show `==> Your service is live 🎉`, jump over to Discord and type your **`!sync`** command.

With that broken string fixed, Render will cleanly pass right over `audit.py`, successfully grab your leveling files next, and your total command count will finally pop up past 22!
