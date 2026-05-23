import discord
from discord.ext import commands
from discord import app_commands

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # 1. REPLY TO PLAY
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID:
            return

        if message.content.lower() == "play this" and message.reference:
            try:
                target = await message.channel.fetch_message(message.reference.message_id)
                if target.attachments:
                    await self.play_audio(message, target.attachments[0].url)
                    await message.add_reaction("🎵")
            except Exception as e:
                print(f"Play Error: {e}")

    # 2. VIEW NETWORK
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📡 IDs", color=0x5865F2)
        for g in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in g.voice_channels]
            if vcs: embed.add_field(name=g.name, value="\n".join(vcs)[:1000], inline=False)
        await interaction.followup.send(embed=embed)

    # 3. PLAY BY LINK/ID
    @app_commands.command(name="playvcsound", description="Play by Link or ID")
    async def playvcsound(self, interaction: discord.Interaction, link_or_id: str):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        try:
            # Simple ID extractor
            msg_id = int(link_or_id.split('/')[-1])
            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing file...")
            else:
                await interaction.followup.send("❌ No file found.")
        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`")

    # 4. STOP
    @app_commands.command(name="stop_all_voice", description="Leave all VCs")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 Stopped.", ephemeral=True)

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
