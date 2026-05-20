import discord
from discord import app_commands
from discord.ext import commands
import os
from groq import AsyncGroq

class AI(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.groq_client = AsyncGroq(api_key=os.getenv("GROQ_API_KEY"))
        
        # Dictionary storing conversation history per user
        self.conversations = {}

    @app_commands.command(name="ai", description="Have a continuous, smart conversation with Ly's AI!")
    @app_commands.describe(prompt="What do you want to say or ask?")
    async def ai_ask(self, interaction: discord.Interaction, prompt: str):
        await interaction.response.defer()
        
        user_id = interaction.user.id

        # 1. Initialize memory bank if it's a new conversation
        if user_id not in self.conversations:
            self.conversations[user_id] = [
                {"role": "system", "content": "You are Ly's AI, a helpful, friendly, and witty AI assistant inside a Discord server. Keep your answers conversational and concise."}
            ]

        # 2. Add the user's newest message
        self.conversations[user_id].append({"role": "user", "content": prompt})

        # 3. Trim older history to keep things light (System prompt + last 10 messages)
        if len(self.conversations[user_id]) > 11:
            self.conversations[user_id] = [self.conversations[user_id][0]] + self.conversations[user_id][-10:]

        try:
            # 4. Request completion from Groq
            completion = await self.groq_client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=self.conversations[user_id],
                max_completion_tokens=400
            )
            ai_response = completion.choices[0].message.content

            # 5. Save the AI's response to memory
            self.conversations[user_id].append({"role": "assistant", "content": ai_response})

            # 6. Build the newly branded layout embed
            embed = discord.Embed(title="✨ Ly's AI Core", color=discord.Color.brand_green())
            embed.add_field(name="👤 You", value=prompt, inline=False)
            
            if len(ai_response) > 1000:
                embed.add_field(name="🤖 Ly's AI", value=ai_response[:997] + "...", inline=False)
            else:
                embed.add_field(name="🤖 Ly's AI", value=ai_response, inline=False)
            
            # The requested attribution footer
            embed.set_footer(text="This AI is powered by Groq ⚡")
            await interaction.followup.send(embed=embed)
            
        except Exception as e:
            print(f"Groq Memory Error: {e}")
            await interaction.followup.send("❌ Sorry, something went wrong while trying to process your request.", ephemeral=True)

    @app_commands.command(name="ai_forget", description="Wipe Ly's AI memory of your conversation and start fresh!")
    async def ai_forget(self, interaction: discord.Interaction):
        user_id = interaction.user.id
        if user_id in self.conversations:
            del self.conversations[user_id]
            await interaction.response.send_message("🧠 *Memory wiped clean! Our next conversation will feel like meeting for the first time.*", ephemeral=True)
        else:
            await interaction.response.send_message("❌ I don't currently have any active conversation history saved for you!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(AI(bot))
