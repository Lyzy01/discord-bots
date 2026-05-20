import discord
from discord import app_commands
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="clear", description="Purge a specific amount of chat history")
    @app_commands.describe(amount="Number of messages to delete")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int):
        if amount < 1:
            return await interaction.response.send_message("❌ You must clear at least 1 message!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🧹 Cleaned up `{len(deleted)}` messages successfully!")

    @app_commands.command(name="kick", description="Kick a disruptive user from the server")
    @app_commands.describe(member="Member to remove", reason="Reason for execution")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        await member.kick(reason=reason)
        await interaction.response.send_message(f"👢 **{member.display_name}** has been kicked. Reason: *{reason}*")

    @app_commands.command(name="ban", description="Permanently ban a user from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason specified"):
        await member.ban(reason=reason)
        await interaction.response.send_message(f"🔨 **{member.display_name}** was banned permanently. Reason: *{reason}*")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
