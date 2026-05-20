import discord
from discord import app_commands
from discord.ext import commands
import platform
import time

start_time = time.time()

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's latency")
    async def ping(self, interaction: discord.Interaction):
        ms = round(self.bot.latency * 1000)
        color = discord.Color.green() if ms < 100 else discord.Color.orange()
        embed = discord.Embed(title="🏓 Pong!", description=f"**Latency:** `{ms}ms`", color=color)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="info", description="Show bot information")
    async def info(self, interaction: discord.Interaction):
        up = int(time.time() - start_time)
        h, r = divmod(up, 3600)
        m, s = divmod(r, 60)
        embed = discord.Embed(title="🤖 Bot Information", color=discord.Color.blurple())
        embed.add_field(name="Bot Name", value=self.bot.user.name, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(name="Users", value=len(set(self.bot.get_all_members())), inline=True)
        embed.add_field(name="Uptime", value=f"{h}h {m}m {s}s", inline=True)
        embed.add_field(name="Python", value=platform.python_version(), inline=True)
        embed.add_field(name="discord.py", value=discord.__version__, inline=True)
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Show server information")
    async def serverinfo(self, interaction: discord.Interaction):
        g = interaction.guild
        embed = discord.Embed(title=f"📊 {g.name}", color=discord.Color.blurple())
        embed.add_field(name="Owner", value=g.owner.mention, inline=True)
        embed.add_field(name="Members", value=g.member_count, inline=True)
        embed.add_field(name="Channels", value=len(g.channels), inline=True)
        embed.add_field(name="Roles", value=len(g.roles), inline=True)
        embed.add_field(name="Created", value=g.created_at.strftime("%B %d, %Y"), inline=True)
        if g.icon:
            embed.set_thumbnail(url=g.icon.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="userinfo", description="Show information about a user")
    @app_commands.describe(member="The member to look up")
    async def userinfo(self, interaction: discord.Interaction, member: discord.Member = None):
        m = member or interaction.user
        embed = discord.Embed(title=f"👤 {m.display_name}", color=m.color)
        embed.add_field(name="Username", value=str(m), inline=True)
        embed.add_field(name="ID", value=m.id, inline=True)
        embed.add_field(name="Joined Server", value=m.joined_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Account Created", value=m.created_at.strftime("%B %d, %Y"), inline=True)
        embed.add_field(name="Roles", value=len(m.roles) - 1, inline=True)
        embed.add_field(name="Top Role", value=m.top_role.mention, inline=True)
        embed.set_thumbnail(url=m.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all available commands")
    async def help(self, interaction: discord.Interaction):
        embed = discord.Embed(title="📖 All Commands", description="All available slash commands:", color=discord.Color.blurple())
        embed.add_field(name="🔧 General", value="`/ping` `/info` `/serverinfo` `/userinfo` `/help`", inline=False)
        embed.add_field(name="🔨 Moderation", value="`/ban` `/kick` `/mute` `/unmute` `/clear` `/warn` `/warnings`", inline=False)
        embed.add_field(name="🎵 Music", value="`/play` `/pause` `/resume` `/skip` `/stop` `/queue` `/nowplaying`", inline=False)
        embed.add_field(name="🎮 Fun", value="`/joke` `/8ball` `/coinflip` `/roll` `/meme` `/roast` `/avatar`", inline=False)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
