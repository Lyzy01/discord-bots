import discord
from discord.ext import commands
from discord import app_commands

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. VIEW ALL IDs
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for g in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in g.voice_channels]
            if vcs:
                embed.add_field(name=f"{g.name} ({g.id})", value="\n".join(vcs)[:1000], inline=False)
        await interaction.followup.send(embed=embed)

    # 2. THE MISSING JOIN COMMAND
    @app_commands.command(name="joinvc", description="Join by IDs")
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
                    await channel.connect(self_deaf=True)
                await interaction.followup.send(f"✅ Teleported to `{channel.name}`.")
            else:
                await interaction.followup.send("❌ IDs are incorrect.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 3. PLAY BY LINK OR ID
    @app_commands.command(name="playvcsound", description="Play by Link or ID")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            msg_id = int(input_data.split('/')[-1])
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing...")
            else:
                await interaction.followup.send("❌ No file found.")
        except:
            await interaction.followup.send("❌ Invalid ID/Link.")

    async def play_audio(self, ctx, url):
        guild = ctx.guild
        user = ctx.author if hasattr(ctx, 'author') else ctx.user
        vc = guild.voice_client
        if not vc:
            if user.voice: vc = await user.voice.channel.connect(self_deaf=True)
            else: return
        if vc.is_playing(): vc.stop()
        opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        vc.play(discord.FFmpegPCMAudio(url, **opts))

async def setup(bot):
    await bot.add_cog(Voice(bot))
