import discord
from discord.ext import commands
from discord import app_commands

# YOUR VERIFIED ID
MY_ID = 1366110873248071801 

class Voice(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # --- THE "PLAY THIS" REPLY LISTENER ---
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.id != MY_ID or message.author.bot:
            return

        if message.content.lower() == "play this" and message.reference:
            try:
                target_msg = await message.channel.fetch_message(message.reference.message_id)
                if target_msg.attachments:
                    await self.play_audio(message, target_msg.attachments[0].url)
                    await message.add_reaction("🎵")
            except Exception as e:
                print(f"Error in on_message: {e}")

    # --- THE /playvcsound COMMAND ---
    @app_commands.command(name="playvcsound", description="Owner Only: Play sound from a Link or Message ID")
    @app_commands.describe(input_data="Paste the Message Link or the Message ID here")
    async def playvcsound(self, interaction: discord.Interaction, input_data: str):
        if interaction.user.id != MY_ID:
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)

        try:
            # Clean the input: If it's a link, get the last part (the ID)
            clean_id = input_data.split('/')[-1]
            msg_id = int(clean_id)

            msg = await interaction.channel.fetch_message(msg_id)
            if msg.attachments:
                await self.play_audio(interaction, msg.attachments[0].url)
                await interaction.followup.send(f"🎵 Playing: `{msg.attachments[0].filename}`")
            else:
                await interaction.followup.send("❌ No file found in that message.")

        except Exception as e:
            await interaction.followup.send(f"⚠️ Error: `{e}`. Make sure the bot is in this DM/Server!")

    # --- SHARED PLAYING LOGIC ---
    async def play_audio(self, ctx_or_inter, url):
        guild = ctx_or_inter.guild
        user = ctx_or_inter.author if hasattr(ctx_or_inter, 'author') else ctx_or_inter.user
        vc = guild.voice_client
        
        if not vc:
            if user.voice:
                vc = await user.voice.channel.connect(self_deaf=True, reconnect=True)
            else: return

        if vc.is_playing(): vc.stop()
        ffmpeg_opts = {'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 'options': '-vn'}
        vc.play(discord.FFmpegPCMAudio(url, **ffmpeg_opts))

    # --- UTILITIES ---
    @app_commands.command(name="viewvoice", description="List IDs")
    async def viewvoice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="📡 Network IDs", color=0x5865F2)
        for guild in self.bot.guilds:
            vcs = [f"`{c.id}` - {c.name}" for c in guild.voice_channels]
            if vcs: embed.add_field(name=guild.name, value=f"ID: `{guild.id}`\n" + "\n".join(vcs)[:1000], inline=False)
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="stop_all_voice", description="Kill all bots")
    async def stop_all_voice(self, interaction: discord.Interaction):
        if interaction.user.id != MY_ID: return
        for vc in self.bot.voice_clients:
            await vc.disconnect(force=True)
        await interaction.response.send_message("🚨 Bots cleared.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Voice(bot))
