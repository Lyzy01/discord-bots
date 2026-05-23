import discord
from discord.ext import commands
from discord import app_commands

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. THE "REPLY TO PLAY" LOGIC
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return

        # Triggered when you reply to an audio file with "play this"
        if message.content.lower() == "play this" and message.reference:
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            
            if replied_msg.attachments:
                attachment = replied_msg.attachments[0]
                if attachment.filename.endswith(('.mp3', '.wav', '.ogg')):
                    
                    # Connect to voice if not already there
                    if not message.guild.voice_client:
                        if message.author.voice:
                            await message.author.voice.channel.connect()
                        else:
                            return await message.channel.send("❌ You need to be in a voice channel first!")

                    vc = message.guild.voice_client
                    if vc.is_playing():
                        vc.stop()

                    # Stream the audio directly
                    vc.play(discord.FFmpegPCMAudio(attachment.url))
                    await message.add_reaction("🎵")

    # 2. REMOTE JOIN COMMAND
    @app_commands.command(name="join_remote", description="Owner only: Force bot into a specific voice channel")
    async def join_remote(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        # Optional: Add a check here to ensure only YOU can use this
        guild = self.bot.get_guild(int(server_id))
        channel = guild.get_channel(int(channel_id))
        
        if guild and channel:
            await channel.connect()
            await interaction.response.send_message(f"✅ Teleported to {channel.name} in {guild.name}")
        else:
            await interaction.response.send_message("❌ Could not find that server or channel.")

    # 3. LEAVE COMMAND
    @app_commands.command(name="leave", description="Make the bot leave voice")
    async def leave(self, interaction: discord.Interaction):
        if interaction.guild.voice_client:
            await interaction.guild.voice_client.disconnect()
            await interaction.response.send_message("👋 Disconnected.")
        else:
            await interaction.response.send_message("❌ I'm not in voice!")

async def setup(bot):
    await bot.add_cog(Voice(bot))
