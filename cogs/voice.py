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

    # 1. VIEW IDs
    @app_commands.command(name="viewvoice", description="List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        msg = "**📋 SERVER AND CHANNEL IDs**\n\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **ID:** `{c.id}`\n"
            msg += "\n"
        await interaction.followup.send(msg[:2000])

    # 2. JOIN VC
    @app_commands.command(name="joinvc", description="Owner Only: Force join a channel")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            guild = self.bot.get_guild(int(server_id.strip()))
            channel = self.bot.get_channel(int(channel_id.strip()))
            
            if not guild or not channel:
                return await interaction.followup.send("❌ Could not find that Server or Channel.")
            
            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True)
            await interaction.followup.send(f"✅ Joined `{channel.name}`!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. PLAY SOUND
    @app_commands.command(name="playvcsound", description="Play sound in a specific server")
    async def playvcsound(self, interaction: discord.Interaction, server_id: str, message_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = self.bot.get_guild(int(server_id.strip()))
            if not guild or not guild.voice_client:
                return await interaction.followup.send("❌ Bot is not in a VC in that server.")

            msg_id = int(message_id.split('/')[-1].strip())
            # Search for the message to get the audio URL
            msg = await interaction.channel.fetch_message(msg_id)
            
            if not msg or not msg.attachments:
                return await interaction.followup.send("❌ No file found in that message.")

            await self.play_audio(guild.voice_client, msg.attachments[0].url)
            await interaction.followup.send(f"🎵 Playing sound in `{guild.name}`")
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. AUDIO ENGINE
    async def play_audio(self, vc, url):
        import ffdl
        if not os.path.exists(self.ffmpeg_path):
            ffdl.install()
        
        if vc.is_playing(): vc.stop()
        opts = {'before_options': '-reconnect 1 -reconnect_streamed 1', 'options': '-vn'}
        vc.play(discord.FFmpegPCMAudio(url, executable=self.ffmpeg_path, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
