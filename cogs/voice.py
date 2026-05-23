import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# --- CONFIGURATION ---
# REPLACE WITH YOUR ACTUAL ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Context Menu: Right-click a message -> Apps -> Play this Sound
        self.ctx_menu = app_commands.ContextMenu(
            name='Play this Sound',
            callback=self.play_context_menu,
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def cog_unload(self):
        self.bot.tree.remove_command(self.ctx_menu.name, type=self.ctx_menu.type)

    # --- 1. THE RIGHT-CLICK "PLAY" LOGIC ---
    async def play_context_menu(self, interaction: discord.Interaction, message: discord.Message):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Owner only.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        if not message.attachments:
            return await interaction.followup.send("❌ This message has no audio file.")
        
        attachment = message.attachments[0]
        if not attachment.filename.endswith(('.mp3', '.wav', '.ogg', '.m4a')):
            return await interaction.followup.send("❌ File type not supported.")

        vc = interaction.guild.voice_client
        if not vc:
            if interaction.user.voice:
                vc = await interaction.user.voice.channel.connect(self_deaf=True, reconnect=True)
            else:
                return await interaction.followup.send("❌ Join a VC first!")

        if vc.is_playing(): vc.stop()
        
        ffmpeg_opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        
        vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
        await interaction.followup.send(f"🎵 Playing: `{attachment.filename}`")

    # --- 2. VIEW NETWORK (ID BASED) ---
    @app_commands.command(name="viewvoice", description="List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vclist = [f"`{c.id}` - {c.name}" for c in guild.voice_channels]
            if vclist:
                val = "\n".join(vclist)
                embed.add_field(name=f"🏰 {guild.name[:20]} (`{guild.id}`)", value=val[:1024], inline=False)
            if len(embed.fields) >= 20: break
        
        await interaction.followup.send(embed=embed)

    # --- 3. JOIN BY ID ---
    @app_commands.command(name="joinvc", description="Force join a VC via IDs")
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

    # --- 4. VOLUME CONTROL ---
    @app_commands.command(name="volume", description="Set bot volume (1-200)")
    async def volume(self, interaction: discord.Interaction, level: int):
        if interaction.user.id != MY_ID: return
        vc = interaction.guild.voice_client
        if vc and vc.source:
            # Wrap the source in a volume transformer if not already
            if not isinstance(vc.source, discord.PCMVolumeTransformer):
                vc.source = discord.PCMVolumeTransformer(vc.source)
            
            vc.source.volume = level / 100
            await interaction.response.send_message(f"🔊 Volume set to {level}%", ephemeral=True)
        else:
            await interaction.response.send_message("❌ Nothing is playing.", ephemeral=True)

    # --- 5. GLOBAL DISCONNECT ---
    @app_commands.command(name="stop_all_voice", description="Kill all voice connections")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.followup.send("🚨 All bots disconnected.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
