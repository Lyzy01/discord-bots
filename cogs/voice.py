import discord
from discord.ext import commands
from discord import app_commands
import asyncio # Crucial for handling timeouts

# REPLACE WITH YOUR ACTUAL ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. THE PERMANENT STAY LOGIC (Background Checker) ---
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        # If the bot is moved or kicked by a non-owner, try to stay put
        if member.id == self.bot.user.id and after.channel is None:
            # We don't auto-reconnect here yet to avoid infinite loops, 
            # but this is where we track if the bot was forced out.
            print(f"Bot was disconnected from {before.channel}")

    # --- 2. THE DM & REPLY LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        if isinstance(message.channel, discord.DMChannel) and message.content.lower() == "join":
            for guild in self.bot.guilds:
                member = guild.get_member(MY_ID)
                if member and member.voice:
                    # self_deaf=True is the "secret sauce" to stop Discord kicks
                    await member.voice.channel.connect(self_deaf=True, reconnect=True)
                    await message.channel.send(f"✅ Anchored in **{member.voice.channel.name}**.")
                    return

        if message.reference and message.content.lower() == "play this":
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            if replied_msg.attachments:
                attachment = replied_msg.attachments[0]
                vc = message.guild.voice_client
                if not vc:
                    vc = await message.author.voice.channel.connect(self_deaf=True, reconnect=True)
                
                if vc.is_playing(): vc.stop()
                
                # Optimized FFmpeg for Render's network to prevent "silence" drops
                ffmpeg_opts = {
                    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
                    'options': '-vn'
                }
                vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
                await message.add_reaction("🎵")

    # --- 3. THE COMMANDS ---
    @app_commands.command(name="viewvoice", description="Scan all servers for VCs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        embed = discord.Embed(title="📡 Voice Network", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = [c.name for c in guild.voice_channels]
            if vcs: embed.add_field(name=guild.name, value=f"`{', '.join(vcs)}`", inline=False)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="joinvc", description="Force join a server/channel")
    async def joinvc(self, interaction: discord.Interaction, server_name: str, channel_name: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        guild = discord.utils.get(self.bot.guilds, name=server_name)
        channel = discord.utils.get(guild.voice_channels, name=channel_name) if guild else None
        
        if channel:
            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True, reconnect=True)
            await interaction.followup.send(f"✅ Permanently joined `{channel_name}` in `{server_name}`.")
        else:
            await interaction.followup.send("❌ Channel or Server not found. Use `/viewvoice` to check names.")

    @app_commands.command(name="stop_all_voice", description="Global Disconnect")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 All voice connections closed.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
