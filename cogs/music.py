import discord
from discord import app_commands
from discord.ext import commands

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="play", description="[Placeholder] Stream music into your voice channel")
    @app_commands.describe(query="Song title or URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.send_message(f"🎵 Music Engine Core initialization request received for: `{query}`. (Voice channels setup pending config).")

async def setup(bot):
    await bot.add_cog(Music(bot))
