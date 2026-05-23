import discord
from discord.ext import commands
from discord import app_commands
import asyncio
import os

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.ffmpeg_path = "./ffmpeg"

    # 1. THE "PLAY THIS" REPLY LISTENER
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        if message.content.lower() == "play this" and message.reference:
            try:
                target_msg = await message.channel.fetch_message(message.reference.message_id)
                if target_msg.attachments:
                    url = target_msg.attachments[0].url
                    await self.play_audio(message, url)
                    await message.add_reaction("🎵")
            except Exception as e:
                print(f"Listener Error: {e}")

    # 2. JOIN VC BY ID (REWRITTEN FOR ACCURACY)
    @app_commands.command(name="joinvc", description="Join a specific server and channel")
    @app_commands.describe(server_id="Copy the Server ID from /viewvoice", channel_id="Copy the Channel ID from /viewvoice")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        try:
            # Convert strings to integers strictly
            s_id = int(server_id.strip())
            c_id = int(channel_id.strip())

            guild = self.bot.get_guild(s_id)
            if not guild:
                return await interaction.followup.send(f"❌ I am not in a server with ID: `{s_id}`")

            channel = guild.get_channel(c_id) or self.bot.get_channel(c_id)
            if not channel or not isinstance(channel, discord.VoiceChannel):
                return await interaction.followup.send(f"❌ I couldn't find a Voice Channel with ID: `{c_id}`")
            
            if guild.voice_client:
                await guild.voice_client.move_to(channel)
            else:
                await channel.connect(self_deaf=True, reconnect=True)
                
            await interaction.followup.send(f"✅ Successfully joined `{channel.name}` in `{guild.name}`.")
        except ValueError:
            await interaction.followup.send("❌ IDs must be numbers only. Don't include letters or spaces.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. PLAY BY LINK OR ID (REWRITTEN)
    @app_commands.command(name="playvcsound", description="Play sound from Link or Message ID")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            msg_id = int(input_data.split('/')[-1].strip())
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
            else:
                await interaction.followup.send("❌ That message has no file attached.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error finding message: `{e}`")

    # 4. VIEW IDs
    @app_commands.command(name="viewvoice", description="List all server and channel IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📡 Available Voice IDs", color=0x5865F2, description="Copy these carefully!")
        
        for g in self.bot.guilds:
            vcs = [f"VC: `{c.id}` ({c.name})" for c in g.voice_channels]
            if vcs:
                embed.add_field(name=f"Server: {g.name} (`{g.id}`)", value="\n".join(vcs)[:1000], inline=False)
        
        if not embed.fields:
            embed.description = "I don't see any voice channels I can join."
            
        await interaction.followup.send(embed=embed)

    # 5. STOP ALL
    @app_commands.command(name="stop_all_voice", description="Force leave all VCs")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients: await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 All voice connections closed.", ephemeral=True)

    # --- CORE AUDIO ENGINE ---
    async def play_audio(self, ctx_or_inter, url):
        import ffdl
        current_exe = self.ffmpeg_path
        if not os.path.exists(current_exe):
            if os.path.exists("./ffmpeg.exe"):
                current_exe = "./ffmpeg.exe"
            else:
                print("📥 Downloading portable FFmpeg...")
                ffdl.install()
        
        guild = ctx_or_inter.guild
        vc = guild.voice_client
        
        if not vc: return # Should be handled by joinvc first

        if vc.is_playing(): vc.stop()

        opts = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5',
            'options': '-vn'
        }
        vc.play(discord.FFmpegPCMAudio(url, executable=current_exe, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
