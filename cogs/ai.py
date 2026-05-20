import discord
from discord import app_commands
from discord.ext import commands
import os
from groq import AsyncGroq

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Crucial: Uses AsyncGroq so your whole bot doesn't lag/freeze while waiting for a response
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))

    @app_commands.command(name="ai", description="Ask the ultra-fast Groq AI a question!")
    @app_commands.describe(prompt="What do you want to ask the AI?")
    async def ai_ask(self, interaction: discord.Interaction, prompt: str):
        # Slash commands crash if they don't respond in 3 seconds, so we defer immediately
        await interaction.response.defer()
        
        try:
            # Querying Llama 3.3 via Groq API
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are a helpful, witty, and concise AI assistant inside a Discord server."},
                    {"role": "user", "content": prompt}
                ],
                max_completion_tokens=400
            )
            ai_response = completion.choices[0].message.content

            # Building a beautiful Embed for the response
            embed = discord.Embed(title="🤖 Groq AI Core", color=discord.Color.blurple())
            embed.add_field(name="❓ Your Prompt", value=f"*{prompt}*", inline=False)
            
            # Safe truncation because Discord embed fields have a 1024 character limit
            if len(ai_response) > 1000:
                embed.add_field(name="💡 Response", value=ai_response[:997] + "...", inline=False)
            else:
                embed.add_field(name="💡 Response", value=ai_response, inline=False)
            
            embed.set_footer(text="Powered by Groq Inference Engine ⚡")
            
            # Sending the final answer back to the channel
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Groq Error: {e}")
            await interaction.followup.send("❌ Sorry, something went wrong while trying to reach the AI engine.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AI(bot))
