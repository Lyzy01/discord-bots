import discord
from discord.ext import commands
from discord import app_commands

class ServerAudit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server-audit", description="Performs a complete security and health scan of the server.")
    # Sets default Discord integration permission requirement to Manage Guild
    @app_commands.default_permissions(manage_guild=True)
    async def server_audit(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Hard fail-safe check: Require user to have Manage Guild OR be the exact Server Owner
        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != guild.owner_id:
            await interaction.response.send_message(
                "
http://googleusercontent.com/immersive_entry_chip/0

Save this code exactly as it is into your `cogs/audit.py` file, make sure your bot restarts to register the changes, and you're good to go!
