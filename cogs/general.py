import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check the bot's engine latency")
    async def ping(self, interaction: discord.Interaction):
        latency = round(self.bot.latency * 1000)
        embed = discord.Embed(title="🏓 Pong!", description=f"Response time: `{latency}ms`", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="serverinfo", description="Display detailed data about this server")
    async def serverinfo(self, interaction: discord.Interaction):
        guild = interaction.guild
        embed = discord.Embed(title=f"📊 {guild.name} Analysis", color=discord.Color.blue())
        embed.set_thumbnail(url=guild.icon.url if guild.icon else None)
        embed.add_field(name="Owner", value=f"{guild.owner.mention}", inline=True)
        embed.add_field(name="Members", value=f"`{guild.member_count}`", inline=True)
        embed.add_field(name="Created On", value=guild.created_at.strftime("%B %d, %Y"), inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="website", description="Get the link to Ly's AI official tutorial and command guide website!")
    async def website_link(self, interaction: discord.Interaction):
        # This link matches your exact Render app domain URL
        site_url = "https://discord-bots-cny2.onrender.com"
        
        embed = discord.Embed(
            title="🌐 Ly's AI Web Portal", 
            description=f"Click the link below to access our full interactive user manual and command handbook!\n\n🔗 **[Open Official Tutorial Website]({site_url})**", 
            color=discord.Color.brand_green()
        )
        embed.set_footer(text="Hosted live on Render secure clouds ⚡")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(General(bot))
