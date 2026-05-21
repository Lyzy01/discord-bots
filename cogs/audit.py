import discord
from discord.ext import commands
from discord import app_commands

class ServerAudit(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="server-audit", description="Performs a basic server health and security scan.")
    @app_commands.default_permissions(manage_guild=True)
    async def server_audit(self, interaction: discord.Interaction):
        guild = interaction.guild
        
        # Admin / Owner protection check
        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != guild.owner_id:
            await interaction.response.send_message("❌ Error: This command is restricted to server administrators.", ephemeral=True)
            return

        # Gather server numbers
        total_members = guild.member_count
        bots = sum(1 for m in guild.members if m.bot)
        humans = total_members - bots
        
        total_channels = len(guild.channels)
        text_channels = len(guild.text_channels)
        voice_channels = len(guild.voice_channels)

        # Check security level
        verify_level = str(guild.verification_level).upper()

        # Build a completely plain text report
        report = (
            f"📊 **SERVER AUDIT REPORT FOR: {guild.name}**\n"
            f"----------------------------------------\n"
            f"🛡️ **Security Verification Level:** {verify_level}\n\n"
            f"👥 **Member Statistics:**\n"
            f"• Total Members: {total_members}\n"
            f"• Humans: {humans}\n"
            f"• Bots: {bots}\n\n"
            f"📁 **Channel Statistics:**\n"
            f"• Total Channels: {total_channels}\n"
            f"• Text Channels: {text_channels}\n"
            f"• Voice Channels: {voice_channels}\n"
            f"----------------------------------------\n"
            f"✅ Audit Complete!"
        )
        
        await interaction.response.send_message(report)

async def setup(bot):
    await bot.add_cog(ServerAudit(bot))
