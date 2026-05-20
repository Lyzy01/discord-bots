import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import yt_dlp

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
    'default_search': 'scsearch1:',
    'source_address': '0.0.0.0'
}

FFMPEG_OPTIONS = {
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
    'options': '-vn'
}

ytdl = yt_dlp.YoutubeDL(YTDL_OPTIONS)

class MusicPlayerSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)
        self.data = data
        self.title = data.get('title', 'Unknown Title')
        self.url = data.get('webpage_url') or data.get('url', '')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=True):
        loop = loop or asyncio.get_event_loop()
        
        if not (url.startswith("http://") or url.startswith("https://")):
            target_query = f"scsearch1:{url}"
        else:
            target_query = url

        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(target_query, download=not stream))
        
        if 'entries' in data:
            if not data['entries']:
                raise Exception("Could not find any tracks matching that search.")
            data = data['entries'][0]

        filename = data['url']
        return cls(discord.FFmpegPCMAudio(filename, **FFMPEG_OPTIONS), data=data)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(name="play", description="🎵 Stream music into your current voice channel.")
    @app_commands.describe(query="Song title, keywords, or direct audio track link")
    async def play(self, interaction: discord.Interaction, query: str):
        # We use a long defer time since cloud servers need an extra moment to handle voice handshakes
        await interaction.response.defer(ephemeral=False)
        
        if not interaction.user.voice or not interaction.user.voice.channel:
            await interaction.followup.send("❌ You must connect to a valid voice channel before deploying the music engine.")
            return

        voice_channel = interaction.user.voice.channel
        voice_client = interaction.guild.voice_client

        try:
            # If the bot is stuck in a weird half-connected state, clear it out completely first
            if voice_client and not voice_client.is_connected():
                try:
                    await voice_client.disconnect(force=True)
                except:
                    pass
                voice_client = None

            # Connect fresh or move smoothly
            if voice_client is None:
                voice_client = await voice_channel.connect(timeout=20.0, reconnect=True)
                await asyncio.sleep(2.0)  # Give Discord plenty of time to set up the region routing
            elif voice_client.channel != voice_channel:
                await voice_client.move_to(voice_channel)
                await asyncio.sleep(2.0)

            # Start fetching the audio track information
            player = await MusicPlayerSource.from_url(query, loop=self.bot.loop, stream=True)
            
            # Stop any overlapping audio tracks if something is already playing
            if voice_client.is_playing():
                voice_client.stop()

            # Final check to make sure the gateway connection didn't drop during extraction
            if not voice_client.is_connected():
                await voice_client.disconnect(force=True)
                voice_client = await voice_channel.connect(timeout=20.0, reconnect=True)
                await asyncio.sleep(2.0)

            voice_client.play(player, after=lambda e: print(f"Audio stream notification: {e}") if e else None)
            
            embed = discord.Embed(
                title="🎶 Now Playing Audio",
                description=f"[{player.title}]({player.url})",
                color=discord.Color.brand_green()
            )
            embed.set_footer(text=f"Requested by: {interaction.user.name} | Audio source platform supported")
            await interaction.followup.send(embed=embed)

        except Exception as e:
            await interaction.followup.send(f"⚠️ **Audio Stream Extraction Failure:** `{e}`")

    @app_commands.command(name="stop", description="🛑 Halt audio playback and disconnect from voice.")
    async def stop(self, interaction: discord.Interaction):
        voice_client = interaction.guild.voice_client
        if voice_client and voice_client.is_connected():
            await voice_client.disconnect()
            await interaction.response.send_message("🛑 **Playback Terminated:** Left the voice channel corridor cleanly.")
        else:
            await interaction.response.send_message("❌ The music engine is not currently connected to any active voice paths.", ephemeral=True)

async def setup(bot: commands.Bot):
    await bot.add_cog(Music(bot))
