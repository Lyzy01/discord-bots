import discord
from discord.ext import commands
from discord import app_commands
import aiohttp
import os

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. VIEW IDs
    @app_commands.command(name="viewvoice", description="Show Server and Channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        msg = "**📋 VOICE IDs**\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
        await interaction.followup.send(msg[:2000])

    # 2. JOIN VC
    @app_commands.command(name="joinvc", description="Make the bot join a specific VC")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            guild = self.bot.get_guild(int(server_id.strip()))
            channel = self.bot.get_channel(int(channel_id.strip()))
            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True)
            await interaction.followup.send(f"✅ Joined `{channel.name}`!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. SPEAK (Using Web API - No local gTTS needed!)
    @app_commands.command(name="speak", description="Speak using TikTok's free TTS engine")
    async def speak(self, interaction: discord.Interaction, server_id: str, my_words: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = self.bot.get_guild(int(server_id.strip()))
            if not guild or not guild.voice_client:
                return await interaction.followup.send("❌ Bot is not in VC. Use /joinvc first!")

            # Use a free public API for TTS (TikTok Voice engine)
            api_url = f"https://api.scrim.network/tts?text={my_words.replace(' ', '%20')}&voice=en_us_001"
            
            # Play directly from the URL
            vc = guild.voice_client
            if vc.is_playing(): vc.stop()
            
            # This uses the built-in FFmpeg player with the Web URL
            # Note: We still need ffmpeg on Render, which is standard.
            vc.play(discord.FFmpegPCMAudio(api_url))
            await interaction.followup.send(f"🎙️ Speaking: {my_words}")
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ Voice Error: `{e}`")

async def setup(bot):
    await bot.add_cog(Voice(bot))
