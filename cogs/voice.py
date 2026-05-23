import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# REPLACE THIS with your actual Discord User ID (Right-click your name -> Copy ID)
MY_ID = 123456789012345678 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- 1. THE DM & REPLY LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        # Only listen to YOU
        if message.author.id != MY_ID or message.author.bot:
            return

        # A. DM CONTROLS
        if isinstance(message.channel, discord.DMChannel):
            cmd = message.content.lower()
            
            if cmd == "join":
                found = False
                for guild in self.bot.guilds:
                    member = guild.get_member(MY_ID)
                    if member and member.voice:
                        await member.voice.channel.connect()
                        await message.channel.send(f"✅ Teleported to **{member.voice.channel.name}** in **{guild.name}**!")
                        found = True
                        break
                if not found:
                    await message.channel.send("❌ Join a voice channel first, then DM me 'join'.")

            elif cmd == "leave":
                for vc in self.bot.voice_clients:
                    await vc.disconnect()
                await message.channel.send("👋 Disconnected from all channels.")

        # B. REPLY TO PLAY LOGIC (In Servers)
        if message.reference:
            if message.content.lower() == "play this":
                replied_msg = await message.channel.fetch_message(message.reference.message_id)
                if replied_msg.attachments:
                    attachment = replied_msg.attachments[0]
                    if attachment.filename.endswith(('.mp3', '.wav', '.ogg')):
                        vc = message.guild.voice_client
                        if not vc:
                            if message.author.voice:
                                vc = await message.author.voice.channel.connect()
                            else:
                                return await message.channel.send("❌ Join voice first!")
                        
                        if vc.is_playing(): vc.stop()
                        vc.play(discord.FFmpegPCMAudio(attachment.url))
                        await message.add_reaction("🎵")

    # --- 2. VIEW ALL VOICE CHANNELS ACROSS SERVERS ---
    @app_commands.command(name="viewvoice", description="Owner Only: Scan all servers for voice channels")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)

        embed = discord.Embed(title="📡 Voice Network Scan", color=discord.Color.blue())
        for guild in self.bot.guilds:
            vcs = [c.name for c in guild.voice_channels]
            if vcs:
                embed.add_field(name=f"🏰 {guild.name}", value=f"Channels: `{', '.join(vcs)}`", inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

    # --- 3. JOIN BY NAME ---
    @app_commands.command(name="joinvc", description="Owner Only: Join a specific VC by name")
    async def joinvc(self, interaction: discord.Interaction, channel_name: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)

        target_channel = None
        for guild in self.bot.guilds:
            target_channel = discord.utils.get(guild.voice_channels, name=channel_name)
            if target_channel:
                break
        
        if target_channel:
            # If already in a voice client in that guild, move; otherwise, connect
            if target_channel.guild.voice_client:
                await target_channel.guild.voice_client.move_to(target_channel)
            else:
                await target_channel.connect()
            await interaction.response.send_message(f"✅ Joined `{channel_name}` in `{target_channel.guild.name}`")
        else:
            await interaction.response.send_message(f"❌ Could not find a channel named `{channel_name}` anywhere.")

    # --- 4. GLOBAL LEAVE ---
    @app_commands.command(name="stop_all_voice", description="Owner Only: Force leave all voice channels")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect()
        await interaction.response.send_message("🚨 All voice connections terminated.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
