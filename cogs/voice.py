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

    # 1. VIEW IDs (To get the numbers you need)
    @app_commands.command(name="viewvoice", description="List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        msg = "**📋 SERVER AND CHANNEL IDs**\n\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name} | **SERVER ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"  ↳ VC: `{c.name}` | **VC ID:** `{c.id}`\n"
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
    @app_commands.command(name="playvcsound", description="Play sound from Link or Message ID")
    async def playvcsound(self, interaction: discord.Interaction, message_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            msg_id = int(message_id.split('/')[-1].strip())
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
            else:
                await interaction.followup.send("❌ No file attached.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. AUDIO ENGINE (Simplified to prevent crashes)
    async def play_audio(self, ctx_or_inter, url):
        guild = ctx_or_inter.guild
        vc = guild.voice_client
        if not vc: return

        if vc.is_playing(): vc.stop()

        # Attempt to use ffdl only when playing
        try:
            import ffdl
            if not os.path.exists(self.ffmpeg_path):
                ffdl.install()
            
            opts = {'before_options': '-reconnect 1 -reconnect_streamed 1', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(url, executable=self.ffmpeg_path, **opts))
        except Exception as e:
            print(f"Audio Error: {e}")

async def setup(bot):
    await bot.add_cog(Voice(bot))
