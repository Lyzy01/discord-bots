import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp
import os

# Optimize yt-dlp parameters for fast stream extraction
YTDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'
}

# Standard FFmpeg streaming flags
FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicPlayerSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        
        if 'entries' in data:
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="play", description="🎵 Stream music into your current voice channel using text searches or links.")
    @app_commands.describe(query="Song title, keywords, or direct video URL")
    async def play(self, interaction: discord.Interaction, query: str):
        await interaction.response.defer(ephemeral=False)
        
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You must connect to a valid voice channel before deploying the music engine.")
            return

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        if voice_client is None:
            voice_client = await voice_channel.connect()
        elif voice_client.channel != voice_channel:
            await voice_client.move_to(voice_channel)

        try:
            player = await MusicPlayerSource.from_url(query, loop=self.bot.loop, stream=True)
            
            if voice_client.is_playing():
                voice_client.stop()

            voice_client.play(player, after=lambda e: print(f"Player error tracking alert: {e}") if e else None)
            
            embed = discord.Embed(
                title="🎶 Now Streaming Audio",
                description=f"[{player.title}]({player.url})",
                color=discord.Color.brand_green()
            )
            embed.set_footer(text=f"Requested by: {interaction.user.name}")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"⚠️ **Audio Stream Extraction Failure:** `{e}`")

    @app_commands.command(name="stop", description="🛑 Halt audio playback and disconnect the voice interface.")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("🛑 **Playback Terminated:** Left the voice channel corridor cleanly.")
        else:
            await interaction.response.send_message("❌ The music engine is not currently connected to any active voice paths.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
