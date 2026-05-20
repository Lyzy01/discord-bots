import discord
from discord import app_commands
from discord.ext import commands
import random
import aiohttp

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "What do you call fake spaghetti? An impasta!",
            "Why did the scarecrow win an award? He was outstanding in his field!"
        ]
        await interaction.response.send_message(f"😂 **Joke:** {random.choice(jokes)}")

    @app_commands.command(name="vibecheck", description="Run a scientific vibe assessment")
    async def vibecheck(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        score = random.randint(0, 100)
        verdict = "Immaculate Vibe. ✨" if score > 75 else "Decent vibes, needs coffee. ☕" if score > 40 else "Vibe check completely failed. 📉"
        
        embed = discord.Embed(title=f"🧠 Vibe Assessment: {target.display_name}", color=discord.Color.purple())
        embed.add_field(name="Score", value=f"`{score}%`", inline=True)
        embed.add_field(name="Verdict", value=verdict, inline=True)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="slap", description="Playfully slap a member")
    async def slap(self, interaction: discord.Interaction, member: discord.Member):
        await interaction.response.send_message(f"💥 **{interaction.user.display_name}** slaps {member.mention} with a cold, smelly fish! 🐟")

async def setup(bot):
    await bot.add_cog(Fun(bot))
