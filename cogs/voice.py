import discord
from discord.ext import commands
from discord import app_commands

# YOUR UPDATED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. PLAY BY MESSAGE ID ---
    @app_commands.command(name="playvcsound", description="Owner Only: Play sound from a Message ID")
    @app_commands.describe(message_id="Copy the ID of the message that has the MP3 file")
    async def playvcsound(self, interaction: discord.Interaction, message_id: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied: You are not the owner.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        try:
            msg = await interaction.channel.fetch_message(int(message_id))
            
            if not msg.attachments:
                return await interaction.followup.send("❌ No file found in that message!")
            
            attachment = msg.attachments[0]
            
            vc = interaction.guild.voice_client
            if not vc:
                if interaction.user.voice:
                    vc = await interaction.user.voice.channel.connect(self_deaf=True, reconnect=True)
                else:
                    return await interaction.followup.send("❌ Join a Voice Channel first!")

            if vc.is_playing():
                vc.stop()
            
            ffmpeg_opts = {
                'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                'options': '-vn'
            }
            
            vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
            await interaction.followup.send(f"🎵 Now playing: `{attachment.filename}`")
            
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # --- 2. VIEW NETWORK IDs ---
    @app_commands.command(name="viewvoice", description="Owner Only: List all Server and Channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title="📡 Voice Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in guild.voice_channels]
            if vcs:
                embed.add_field(name=guild.name, value=f"Server ID: `{guild.id}`\n" + "\n".join(vcs)[:1000], inline=False)
        
        await interaction.followup.send(embed=embed)

    # --- 3. JOIN BY ID ---
    @app_commands.command(name="joinvc", description="Owner Only: Teleport bot using IDs")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            guild = self.bot.get_guild(int(server_id))
            channel = self.bot.get_channel(int(channel_id))
            if guild and channel:
                if guild.voice_client: await guild.voice_client.move_to(channel)
                else: await channel.connect(self_deaf=True, reconnect=True)
                await interaction.followup.send(f"✅ Joined `{channel.name}` in `{guild.name}`.")
            else:
                await interaction.followup.send("❌ IDs not found. Check `/viewvoice`.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # --- 4. GLOBAL LEAVE ---
    @app_commands.command(name="stop_all_voice", description="Force all bots to leave")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 All voice connections closed.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
