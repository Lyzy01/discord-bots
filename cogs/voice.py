import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# --- CONFIGURATION ---
MY_ID = 1366110873248071801 # MAKE SURE THIS IS YOUR ID

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. VIEW NETWORK ---
    @app_commands.command(name="viewvoice", description="Owner Only: List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vclist = [f"`{c.id}` - {c.name}" for c in guild.voice_channels]
            if vclist:
                val = "\n".join(vclist)
                embed.add_field(name=f"🏰 {guild.name[:20]}", value=f"ID: `{guild.id}`\n{val[:1000]}", inline=False)
            if len(embed.fields) >= 20: break
        
        await interaction.followup.send(embed=embed)

    # --- 2. JOIN BY ID ---
    @app_commands.command(name="joinvc", description="Owner Only: Join via IDs")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = self.bot.get_guild(int(server_id))
            channel = self.bot.get_channel(int(channel_id))
            if guild and channel:
                if guild.voice_client: await guild.voice_client.move_to(channel)
                else: await channel.connect(self_deaf=True, reconnect=True)
                await interaction.followup.send(f"✅ Joined `{channel.name}`.")
            else:
                await interaction.followup.send("❌ IDs not found.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # --- 3. THE PLAY COMMAND (Manual ID entry) ---
    @app_commands.command(name="playvcsound", description="Owner Only: Play sound from a Message ID")
    async def playvcsound(self, interaction: discord.Interaction, message_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            if not msg.attachments:
                return await interaction.followup.send("❌ No file found in that message.")
            
            attachment = msg.attachments[0]
            vc = interaction.guild.voice_client
            if not vc:
                if interaction.user.voice:
                    vc = await interaction.user.voice.channel.connect(self_deaf=True, reconnect=True)
                else: return await interaction.followup.send("❌ Join a VC first!")

            if vc.is_playing(): vc.stop()
            
            ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
            vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
            await interaction.followup.send(f"🎵 Playing: `{attachment.filename}`")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # --- 4. GLOBAL DISCONNECT ---
    @app_commands.command(name="stop_all_voice", description="Kill all voice connections")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.followup.send("🚨 All bots disconnected.")

# This function registers the cog and the Context Menu separately to avoid sync errors
async def setup(bot):
    cog = Voice(bot)
    await bot.add_cog(cog)

    # Adding the Context Menu (Right-click message -> Apps -> Play this Sound)
    @bot.tree.context_menu(name="Play this Sound")
    async def play_sound_context(interaction: discord.Interaction, message: discord.Message):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        if not message.attachments:
            return await interaction.followup.send("❌ No audio file found.")
        
        attachment = message.attachments[0]
        vc = interaction.guild.voice_client
        if not vc:
            if interaction.user.voice:
                vc = await interaction.user.voice.channel.connect(self_deaf=True, reconnect=True)
            else: return await interaction.followup.send("❌ Join a VC first!")

        if vc.is_playing(): vc.stop()
        ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
        await interaction.followup.send(f"🎵 Playing: `{attachment.filename}`")
