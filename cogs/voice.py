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

    @app_commands.command(name="speak", description="Bot speaks in the VC")
    @app_commands.describe(server_id="ID of the server", my_words="Words to speak")
    async def speak(self, interaction: discord.Interaction, server_id: str, my_words: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            from gtts import gTTS
            import ffdl
            
            guild = self.bot.get_guild(int(server_id.strip()))
            if not guild or not guild.voice_client:
                return await interaction.followup.send("❌ Bot is not in VC. Use /joinvc first.")

            if not os.path.exists(self.ffmpeg_path):
                ffdl.install()

            tts = gTTS(text=my_words, lang='en')
            tts.save("speak.mp3")

            vc = guild.voice_client
            if vc.is_playing(): vc.stop()
            
            vc.play(discord.FFmpegPCMAudio("speak.mp3", executable=self.ffmpeg_path))
            await interaction.followup.send(f"🎙️ Speaking: {my_words}")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @app_commands.command(name="joinvc", description="Join a channel")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            guild = self.bot.get_guild(int(server_id.strip()))
            channel = self.bot.get_channel(int(channel_id.strip()))
            if guild.voice_client: await guild.voice_client.move_to(channel)
            else: await channel.connect(self_deaf=True)
            await interaction.followup.send(f"✅ Joined `{channel.name}`!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        msg = "**📋 IDs**\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
        await interaction.followup.send(msg[:2000])

async def setup(bot):
    await bot.add_cog(Voice(bot))
