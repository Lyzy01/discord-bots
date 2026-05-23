import discord
from discord.ext import commands
from discord import app_commands
import asyncio

# REPLACE WITH YOUR ACTUAL ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        # DM JOIN LOGIC
        if isinstance(message.channel, discord.DMChannel) and message.content.lower() == "join":
            for guild in self.bot.guilds:
                member = guild.get_member(MY_ID)
                if member and member.voice:
                    await member.voice.channel.connect(self_deaf=True, reconnect=True)
                    await message.channel.send(f"✅ Anchored in **{member.voice.channel.name}** ({guild.name}).")
                    return

        # REPLY TO PLAY LOGIC
        if message.reference and message.content.lower() == "play this":
            replied_msg = await message.channel.fetch_message(message.reference.message_id)
            if replied_msg.attachments:
                attachment = replied_msg.attachments[0]
                vc = message.guild.voice_client
                if not vc:
                    if message.author.voice:
                        vc = await message.author.voice.channel.connect(self_deaf=True, reconnect=True)
                    else:
                        return await message.channel.send("❌ Join a VC first!")
                
                if vc.is_playing(): vc.stop()
                ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
                vc.play(discord.FFmpegPCMAudio(attachment.url, **ffmpeg_opts))
                await message.add_reaction("🎵")

    @app_commands.command(name="viewvoice", description="Owner Only: List Servers and IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        
        # FIX: Defer the response so Discord doesn't timeout
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = "\n".join([f"`{c.id}` - {c.name}" for c in guild.voice_channels])
            # Limit to 25 fields for Discord embed limits
            if len(embed.fields) < 25:
                embed.add_field(name=f"{guild.name} (ID: `{guild.id}`)", value=vcs if vcs else "No VCs", inline=False)
        
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="joinvc", description="Owner Only: Join by Server/Channel ID")
    async def joinvc(self, interaction: discord.Interaction, server_id: str, channel_id: str):
        if interaction.user.id != MY_ID: return
        
        # FIX: Defer the response
        await interaction.response.defer(ephemeral=True)
        
        try:
            guild = self.bot.get_guild(int(server_id))
            channel = self.bot.get_channel(int(channel_id))
            
            if guild and channel:
                if guild.voice_client:
                    await guild.voice_client.move_to(channel)
                else:
                    await channel.connect(self_deaf=True, reconnect=True)
                await interaction.followup.send(f"✅ Joined `{channel.name}` in `{guild.name}`.")
            else:
                await interaction.followup.send("❌ Invalid IDs. Use `/viewvoice`.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    @app_commands.command(name="stop_all_voice", description="Global Disconnect")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.followup.send("🚨 All bots cleared.")

async def setup(bot):
    await bot.add_cog(Voice(bot))
