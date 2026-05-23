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

    @app_commands.command(name="speak", description="Speak in a specific Server and Channel")
    @app_commands.describe(
        server_id="The ID of the server", 
        channel_id="The ID of the voice channel", 
        my_words="What the bot should say"
    )
    async def speak(self, interaction: discord.Interaction, server_id: str, channel_id: str, my_words: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            # --- AUTO-INSTALLER SECTION ---
            try:
                import ffdl
                from gtts import gTTS
            except ImportError:
                # If Render forgot them, we install them manually right now
                subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-downloader", "gTTS"])
                import ffdl
                from gtts import gTTS

            # Find the server and channel
            guild = self.bot.get_guild(int(server_id.strip()))
            channel = self.bot.get_channel(int(channel_id.strip()))

            if not guild or not channel:
                return await interaction.followup.send("❌ Invalid Server or Channel ID.")

            # Connect to voice
            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True)

            # Prepare FFmpeg
            if not os.path.exists(self.ffmpeg_path):
                ffdl.install()

            # Create and play speech
            tts = gTTS(text=my_words, lang='en')
            tts.save("speak.mp3")
            
            vc = guild.voice_client
            if vc.is_playing(): vc.stop()
            vc.play(discord.FFmpegPCMAudio("speak.mp3", executable=self.ffmpeg_path))
            
            await interaction.followup.send(f"🎙️ Joined `{channel.name}` and speaking: {my_words}")

        except Exception as e:
            await interaction.followup.send(f"⚠️ Voice Error: `{e}`")

    @app_commands.command(name="viewvoice", description="Show IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        msg = "**📋 VOICE IDs**\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
        await interaction.followup.send(msg[:2000])

async def setup(bot):
    await bot.add_cog(Voice(bot))
