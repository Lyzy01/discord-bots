import discord
from discord import app_commands
from discord.ext import commands
import yt_dlp
import asyncio
from collections import deque

YTDL_OPTS = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',
}

FFMPEG_OPTS = {
    'options': '-vn',
    'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
}

queues: dict[int, deque] = {}
now_playing: dict[int, dict] = {}

class Music(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def get_queue(self, guild_id: int) -> deque:
        queues.setdefault(guild_id, deque())
        return queues[guild_id]

    async def fetch_song(self, query: str) -> dict:
        loop = asyncio.get_event_loop()
        if not query.startswith('http'):
            query = f"ytsearch:{query}"
        with yt_dlp.YoutubeDL(YTDL_OPTS) as ydl:
            data = await loop.run_in_executor(None, lambda: ydl.extract_info(query, download=False))
        if 'entries' in data:
            data = data['entries'][0]
        duration = data.get('duration', 0)
        mins, secs = divmod(duration, 60)
        return {
            'url': data['url'],
            'title': data.get('title', 'Unknown'),
            'duration': f"{mins}:{secs:02d}" if duration else "Unknown",
            'thumbnail': data.get('thumbnail', ''),
            'webpage_url': data.get('webpage_url', ''),
        }

    def play_next(self, guild_id: int, voice_client: discord.VoiceClient):
        queue = self.get_queue(guild_id)
        if queue and voice_client and voice_client.is_connected():
            song = queue.popleft()
            now_playing[guild_id] = song
            source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTS)
            voice_client.play(source, after=lambda e: self.play_next(guild_id, voice_client))
        else:
            now_playing.pop(guild_id, None)

    @app_commands.command(name="play", description="Play a song from YouTube")
    @app_commands.describe(query="Song name or YouTube URL")
    async def play(self, interaction: discord.Interaction, query: str):
        if not interaction.user.voice:
            return await interaction.response.send_message("❌ Join a voice channel first!", ephemeral=True)
        await interaction.response.defer()
        vc = interaction.guild.voice_client
        if not vc:
            vc = await interaction.user.voice.channel.connect()
        elif vc.channel != interaction.user.voice.channel:
            await vc.move_to(interaction.user.voice.channel)
        try:
            song = await self.fetch_song(query)
            if vc.is_playing() or vc.is_paused():
                self.get_queue(interaction.guild.id).append(song)
                embed = discord.Embed(title="➕ Added to Queue", description=f"[{song['title']}]({song['webpage_url']})", color=discord.Color.blue())
                embed.add_field(name="Position", value=f"#{len(self.get_queue(interaction.guild.id))}")
                embed.add_field(name="Duration", value=song['duration'])
            else:
                now_playing[interaction.guild.id] = song
                source = discord.FFmpegPCMAudio(song['url'], **FFMPEG_OPTS)
                vc.play(source, after=lambda e: self.play_next(interaction.guild.id, vc))
                embed = discord.Embed(title="🎵 Now Playing", description=f"[{song['title']}]({song['webpage_url']})", color=discord.Color.green())
                embed.add_field(name="Duration", value=song['duration'])
                if song['thumbnail']:
                    embed.set_thumbnail(url=song['thumbnail'])
            await interaction.followup.send(embed=embed)
        except Exception as e:
            await interaction.followup.send(f"❌ Error: {e}")

    @app_commands.command(name="pause", description="Pause the current song")
    async def pause(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_playing():
            vc.pause()
            await interaction.response.send_message("⏸️ Paused!")
        else:
            await interaction.response.send_message("❌ Nothing is playing!", ephemeral=True)

    @app_commands.command(name="resume", description="Resume the paused song")
    async def resume(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and vc.is_paused():
            vc.resume()
            await interaction.response.send_message("▶️ Resumed!")
        else:
            await interaction.response.send_message("❌ Nothing is paused!", ephemeral=True)

    @app_commands.command(name="skip", description="Skip the current song")
    async def skip(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc and (vc.is_playing() or vc.is_paused()):
            vc.stop()
            await interaction.response.send_message("⏭️ Skipped!")
        else:
            await interaction.response.send_message("❌ Nothing to skip!", ephemeral=True)

    @app_commands.command(name="stop", description="Stop music and disconnect")
    async def stop(self, interaction: discord.Interaction):
        vc = interaction.guild.voice_client
        if vc:
            queues[interaction.guild.id] = deque()
            now_playing.pop(interaction.guild.id, None)
            vc.stop()
            await vc.disconnect()
            await interaction.response.send_message("⏹️ Stopped and disconnected!")
        else:
            await interaction.response.send_message("❌ Not in a voice channel!", ephemeral=True)

    @app_commands.command(name="queue", description="Show the music queue")
    async def queue_cmd(self, interaction: discord.Interaction):
        queue = self.get_queue(interaction.guild.id)
        embed = discord.Embed(title="🎵 Music Queue", color=discord.Color.blurple())
        current = now_playing.get(interaction.guild.id)
        if current:
            embed.add_field(name="▶️ Now Playing", value=current['title'], inline=False)
        if not queue:
            embed.add_field(name="📭 Up Next", value="Queue is empty — use `/play` to add songs!", inline=False)
        else:
            songs = list(queue)[:10]
            embed.add_field(name=f"📋 Up Next ({len(queue)} songs)", value="\n".join(f"`{i+1}.` {s['title']}" for i, s in enumerate(songs)), inline=False)
            if len(queue) > 10:
                embed.set_footer(text=f"...and {len(queue) - 10} more")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="nowplaying", description="Show the currently playing song")
    async def nowplaying(self, interaction: discord.Interaction):
        song = now_playing.get(interaction.guild.id)
        if not song:
            return await interaction.response.send_message("❌ Nothing is playing right now!")
        embed = discord.Embed(title="🎵 Now Playing", description=f"[{song['title']}]({song['webpage_url']})", color=discord.Color.green())
        embed.add_field(name="Duration", value=song['duration'])
        if song['thumbnail']:
            embed.set_thumbnail(url=song['thumbnail'])
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Music(bot))
