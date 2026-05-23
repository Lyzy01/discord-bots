import discord
from discord.ext import commands
from discord import app_commands
import os
import sys
import subprocess

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_path = "./ffmpeg"

    # 1. VIEW IDs
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        msg = "**📋 IDs**\n\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
        await interaction.followup.send(msg[:2000])

    # 2. JOIN VC
    @app_commands.command(name="joinvc", description="Join a channel")
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

    # 3. PLAY TTS
    @app_commands.command(name="playvctts", description="Bot speaks your words")
    async def playvctts(self, interaction: discord.Interaction, server_id: str, my_words: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Import gTTS here to prevent boot-up crashes
            from gtts import gTTS
            
            guild = self.bot.get_guild(int(server_id.strip()))
            if not guild or not guild.voice_client:
                return await interaction.followup.send("❌ Bot not in VC.")

            tts = gTTS(text=my_words, lang='en')
            tts.save("tts.mp3")

            await self.play_audio(guild.voice_client, "tts.mp3")
            await interaction.followup.send(f"🗣️ Speaking in `{guild.name}`")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. AUDIO ENGINE
    async def play_audio(self, vc, filename):
        try:
            import ffdl
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-downloader"])
            import ffdl
            
        if not os.path.exists(self.ffmpeg_path):
            ffdl.install()
        
        if vc.is_playing(): vc.stop()
        vc.play(discord.FFmpegPCMAudio(filename, executable=self.ffmpeg_path))

async def setup(bot):
    await bot.add_cog(Voice(bot))
