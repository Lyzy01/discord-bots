import discord
from discord.ext import commands
from discord import app_commands
import os

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_path = "./ffmpeg"

    # 1. VIEW IDs (Checks if bot sees the servers)
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        msg = "**📋 VOICE IDs**\n\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
        await interaction.followup.send(msg[:2000])

    # 2. JOIN VC (Must be done before speaking)
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
            await interaction.followup.send(f"⚠️ Join Error: `{e}`")

    # 3. SPEAK (The command you want)
    @app_commands.command(name="speak", description="Speak words in the VC")
    async def speak(self, interaction: discord.Interaction, server_id: str, my_words: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            # We import these HERE so the bot doesn't crash on startup
            from gtts import gTTS
            import ffdl
            
            guild = self.bot.get_guild(int(server_id.strip()))
            if not guild or not guild.voice_client:
                return await interaction.followup.send("❌ Join the VC first with /joinvc")

            # Ensure FFmpeg exists
            if not os.path.exists(self.ffmpeg_path):
                ffdl.install()

            # Create speech file
            tts = gTTS(text=my_words, lang='en')
            tts.save("voice.mp3")

            # Play in VC
            vc = guild.voice_client
            if vc.is_playing():
                vc.stop()
            
            vc.play(discord.FFmpegPCMAudio("voice.mp3", executable=self.ffmpeg_path))
            await interaction.followup.send(f"🎙️ Speaking in `{guild.name}`: {my_words}")
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ Voice Error: `{e}`")

async def setup(bot):
    await bot.add_cog(Voice(bot))
