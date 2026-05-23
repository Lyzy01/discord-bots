import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # This is where the bot will store its audio engine
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
                    await self.play_audio(message, url)
                    await message.add_reaction("🎵")
            except Exception as e:
                print(f"Listener Error: {e}")

    # 2. JOIN VC BY ID
    @app_commands.command(name="joinvc", description="Owner Only: Join a specific server and channel")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        try:
            guild = self.bot.get_guild(int(server_id))
            channel = self.bot.get_channel(int(channel_id))
            
            if guild and channel:
                if guild.voice_client:
                    await guild.voice_client.move_to(channel)
                else:
                    await channel.connect(self_deaf=True, reconnect=True)
                await interaction.followup.send(f"✅ Joined `{channel.name}`.")
            else:
                await interaction.followup.send("❌ IDs not found.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. PLAY BY LINK OR ID
    @app_commands.command(name="playvcsound", description="Owner Only: Play sound from Link or Message ID")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            msg_id = int(input_data.split('/')[-1])
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
            else:
                await interaction.followup.send("❌ No file found.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. VIEW IDs
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📡 IDs", color=0x5865F2)
        for g in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in g.voice_channels]
            if vcs: embed.add_field(name=g.name, value="\n".join(vcs)[:1000])
        await interaction.followup.send(embed=embed)

    # 5. STOP ALL
    @app_commands.command(name="stop_all_voice", description="Kill all sessions")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients: await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 Terminated.", ephemeral=True)

    # --- CORE AUDIO ENGINE ---
    async def play_audio(self, ctx_or_inter, url):
        import ffdl
        
        # Check for both './ffmpeg' and './ffmpeg.exe' just in case
        current_exe = self.ffmpeg_path
        if not os.path.exists(current_exe):
            if os.path.exists("./ffmpeg.exe"):
                current_exe = "./ffmpeg.exe"
            else:
                print("📥 Downloading portable FFmpeg...")
                ffdl.install()
        
        guild = ctx_or_inter.guild
        user = ctx_or_inter.author if hasattr(ctx_or_inter, 'author') else ctx_or_inter.user
        vc = guild.voice_client
        
        if not vc:
            if user.voice: 
                vc = await user.voice.channel.connect(self_deaf=True)
            else: 
                return

        if vc.is_playing(): 
            vc.stop()

        opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        vc.play(discord.FFmpegPCMAudio(url, executable=current_exe, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
