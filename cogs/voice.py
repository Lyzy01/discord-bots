import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# REPLACE WITH YOUR ACTUAL ID
MY_ID = 123456789012345678 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. THE DM & REPLY LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        # DM JOIN (Scan all servers for your ID)
        if isinstance(message.channel, discord.DMChannel) and message.content.lower() == "join":
            for guild in self.bot.guilds:
                member = guild.get_member(MY_ID)
                if member and member.voice:
                    await member.voice.channel.connect(self_deaf=True, reconnect=True)
                    await message.channel.send(f"✅ Anchored in **{member.voice.channel.name}** ({guild.name}).")
                    return

        # REPLY TO PLAY
        if message.reference and message.content.lower() == "play this":
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            if replied_msg.attachments:
                attachment = replied_msg.attachments[0]
                vc = message.guild.voice_client
                if not vc:
                    if message.author.voice:
                        vc = await message.author.voice.channel.connect(self_deaf=True, reconnect=True)
                    else:
                        return await message.channel.send("❌ You aren't in a VC!")
                
                if vc.is_playing(): vc.stop()
                
                ffmpeg_opts = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
                await message.add_reaction("🎵")

    # --- 2. THE ID-BASED COMMANDS ---

    @app_commands.command(name="viewvoice", description="Owner Only: List Servers and IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = "\n".join([f"`{c.id}` - {c.name}" for c in guild.voice_channels])
            embed.add_field(
                name=f"{guild.name} (ID: `{guild.id}`)", 
                value=vcs if vcs else "No VCs", 
                inline=False
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="joinvc", description="Owner Only: Join by Server/Channel ID")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = self.bot.get_guild(int(server_id))
            channel = self.bot.get_channel(int(channel_id))
            
            if guild and channel:
                if guild.voice_client:
                    await guild.voice_client.move_to(channel)
                else:
                    await channel.connect(self_deaf=True, reconnect=True)
                await interaction.followup.send(f"✅ Successfully joined `{channel.name}` in `{guild.name}`.")
            else:
                await interaction.followup.send("❌ Could not find that Server ID or Channel ID.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @app_commands.command(name="stop_all_voice", description="Global Disconnect")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 All bots cleared.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
