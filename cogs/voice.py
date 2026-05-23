import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

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
    @app_commands.describe(server_id="ID of the server", channel_id="ID of the voice channel")
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
                await interaction.followup.send(f"✅ Joined `{channel.name}` in `{guild.name}`.")
            else:
                await interaction.followup.send("❌ Could not find Server or Channel ID.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. PLAY BY LINK OR ID
    @app_commands.command(name="playvcsound", description="Owner Only: Play sound from Link or Message ID")
    @app_commands.describe(input_data="Paste the Message Link or Message ID")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        try:
            # Extract ID from end of link or use raw ID
            msg_id = int(input_data.split('/')[-1])
            msg = await interaction.channel.fetch_message(msg_id)
            
            if msg.attachments:
                url = msg.attachments[0].url
                await self.play_audio(interaction, url)
                await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
            else:
                await interaction.followup.send("❌ No file attached to that message.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`. Ensure the bot is in the source channel!")

    # 4. VIEW IDs
    @app_commands.command(name="viewvoice", description="Owner Only: List all accessible IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title="📡 Network Voice IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in guild.voice_channels]
            if vcs:
                embed.add_field(name=f"{guild.name} ({guild.id})", value="\n".join(vcs)[:1000], inline=False)
        
        await interaction.followup.send(embed=embed)

    # 5. STOP & LEAVE ALL
    @app_commands.command(name="stop_all_voice", description="Owner Only: Force leave all VCs")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 All voice sessions terminated.", ephemeral=True)

    # --- CORE AUDIO ENGINE ---
    async def play_audio(self, ctx_or_inter, url):
        guild = ctx_or_inter.guild
        user = ctx_or_inter.author if hasattr(ctx_or_inter, 'author') else ctx_or_inter.user
        
        # Connect if not connected
        vc = guild.voice_client
        if not vc:
            if user.voice:
                vc = await user.voice.channel.connect(self_deaf=True, reconnect=True)
            else:
                return

        # Stop existing audio
        if vc.is_playing():
            vc.stop()

        # Stream settings for high-latency hosts (like Render)
        ffmpeg_options = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }

        # Play audio using the standard FFmpeg source
        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_options))

async def setup(bot):
    await bot.add_cog(Voice(bot))
