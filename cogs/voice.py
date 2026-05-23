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
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            # Clean up the input in case of accidental spaces
            s_id = int(server_id.strip())
            c_id = int(channel_id.strip())

            guild = self.bot.get_guild(s_id)
            if not guild:
                return await interaction.followup.send(f"❌ Server `{s_id}` not found. Am I in that server?")

            # Look for the channel anywhere the bot can see
            channel = self.bot.get_channel(c_id)
            
            if not channel:
                return await interaction.followup.send(f"❌ Channel `{c_id}` not found.")

            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True, reconnect=True)
                
            await interaction.followup.send(f"✅ Joined `{channel.name}`!")
        except Exception as e:
            await interaction.followup.send(f"⚠️ System Error: `{e}`")

    @app_commands.command(name="viewvoice", description="List everything clearly")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        output = "**📋 COPY THESE IDs:**\n\n"
        for g in self.bot.guilds:
            output += f"**SERVER NAME:** {g.name}\n"
            output += f"**SERVER ID:** `{g.id}`\n"
            vcs = [f"  ↳ VC: `{c.name}` | ID: `{c.id}`" for c in g.voice_channels]
            output += "\n".join(vcs) + "\n\n"
        
        await interaction.followup.send(output[:2000])

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
