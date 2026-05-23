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

    @app_commands.command(name="joinvc", description="Owner Only: Force join a channel")
    @app_commands.describe(server_id="The ID of the server", channel_id="The ID of the voice channel")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        try:
            s_id = int(server_id.strip())
            c_id = int(channel_id.strip())

            guild = self.bot.get_guild(s_id)
            if not guild:
                return await interaction.followup.send(f"❌ Server `{s_id}` not found.")

            channel = self.bot.get_channel(c_id)
            if not channel:
                return await interaction.followup.send(f"❌ Channel `{c_id}` not found.")

            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True, reconnect=True)
                
            await interaction.followup.send(f"✅ Joined `{channel.name}`!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @app_commands.command(name="viewvoice", description="List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        msg = "**📋 SERVER AND CHANNEL IDs**\n\n"
        for g in self.bot.guilds:
            msg += f"**SERVER:** {g.name}\n**SERVER ID:** `{g.id}`\n"
            for c in g.voice_channels:
                msg += f"↳ VC: `{c.name}` | **VC ID:** `{c.id}`\n"
            msg += "\n"
        
        await interaction.followup.send(msg[:2000])

    async def play_audio(self, ctx_or_inter, url):
        import ffdl
        if not os.path.exists(self.ffmpeg_path):
            ffdl.install()
        
        guild = ctx_or_inter.guild
        vc = guild.voice_client
        if vc and not vc.is_playing():
            opts = {'before_options': '-reconnect 1 -reconnect_streamed 1', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(url, executable=self.ffmpeg_path, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
