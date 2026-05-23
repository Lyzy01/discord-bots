import discord
from discord.ext import commands
from discord import app_commands
import os
import ffdl # Added explicit import here

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_path = "./ffmpeg"

    # 1. THE "PLAY THIS" REPLY LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        if message.content.lower() == "play this" and message.reference:
            try:
                target_msg = await message.channel.fetch_message(message.reference.message_id)
                if target_msg.attachments:
                    url = target_msg.attachments[0].url
                    # Check if bot is in a VC first
                    if message.guild.voice_client:
                        await self.play_audio(message, url)
                        await message.add_reaction("🎵")
                    else:
                        await message.channel.send("❌ Join a VC first with `/joinvc`")
            except Exception as e:
                print(f"Listener Error: {e}")

    # 2. JOIN VC BY ID
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

    # 3. PLAY BY LINK OR ID
    @app_commands.command(name="playvcsound", description="Play sound from Link or Message ID")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            msg_id = int(input_data.split('/')[-1].strip())
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                if interaction.guild.voice_client:
                    await self.play_audio(interaction, msg.attachments[0].url)
                    await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
                else:
                    await interaction.followup.send("❌ Use `/joinvc` first!")
            else:
                await interaction.followup.send("❌ No file found.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. VIEW IDs
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

    # 5. CORE AUDIO ENGINE
    async def play_audio(self, ctx_or_inter, url):
        if not os.path.exists(self.ffmpeg_path):
            ffdl.install()
        
        guild = ctx_or_inter.guild
        vc = guild.voice_client
        if vc:
            if vc.is_playing():
                vc.stop()
            opts = {'before_options': '-reconnect 1 -reconnect_streamed 1', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(url, executable=self.ffmpeg_path, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
