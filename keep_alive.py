import discord
from discord import app_commands
from discord.ext import commands
import random, aiohttp

JOKES = [
    "Why don't scientists trust atoms? Because they make up everything!",
    "I told my wife she was drawing her eyebrows too high. She looked surprised.",
    "What do you call a fish without eyes? A fsh!",
    "Why did the scarecrow win an award? He was outstanding in his field!",
    "I'm reading a book about anti-gravity. It's impossible to put down!",
    "Why do cows wear bells? Because their horns don't work.",
    "What do you call fake spaghetti? An impasta!",
    "I would tell you a construction joke, but I'm still working on it.",
    "Why can't you give Elsa a balloon? She'll let it go.",
    "Did you hear about the claustrophobic astronaut? He just needed a little space.",
]

ROASTS = [
    "You're the reason they put instructions on shampoo bottles.",
    "I'd agree with you, but then we'd both be wrong.",
    "You have your entire life to be an idiot. Take today off.",
    "If laughter is the best medicine, your face must be curing diseases.",
    "Some people have a way with words. Others... not have way.",
    "You're not stupid; you just have bad luck thinking.",
]

EIGHT_BALL = [
    ("It is certain.", "🟢"), ("It is decidedly so.", "🟢"),
    ("Without a doubt.", "🟢"), ("Yes, definitely.", "🟢"),
    ("You may rely on it.", "🟢"), ("Most likely.", "🟢"),
    ("Outlook good.", "🟢"), ("Yes.", "🟢"), ("Signs point to yes.", "🟢"),
    ("Reply hazy, try again.", "🟡"), ("Ask again later.", "🟡"),
    ("Cannot predict now.", "🟡"), ("Concentrate and ask again.", "🟡"),
    ("Don't count on it.", "🔴"), ("My reply is no.", "🔴"),
    ("My sources say no.", "🔴"), ("Outlook not so good.", "🔴"),
    ("Very doubtful.", "🔴"),
]

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Get a random joke")
    async def joke(self, interaction: discord.Interaction):
        embed = discord.Embed(title="😂 Random Joke", description=random.choice(JOKES), color=discord.Color.yellow())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="8ball", description="Ask the magic 8-ball a question")
    @app_commands.describe(question="Your question")
    async def eightball(self, interaction: discord.Interaction, question: str):
        answer, emoji = random.choice(EIGHT_BALL)
        embed = discord.Embed(title="🎱 Magic 8-Ball", color=discord.Color.dark_blue())
        embed.add_field(name="Question", value=question, inline=False)
        embed.add_field(name="Answer", value=f"{emoji} {answer}", inline=False)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="coinflip", description="Flip a coin!")
    async def coinflip(self, interaction: discord.Interaction):
        result = random.choice(["Heads 🪙", "Tails 🪙"])
        embed = discord.Embed(title="🪙 Coin Flip", description=f"**{result}!**", color=discord.Color.gold())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="roll", description="Roll a dice")
    @app_commands.describe(sides="Number of sides (default: 6)")
    async def roll(self, interaction: discord.Interaction, sides: int = 6):
        if sides < 2:
            return await interaction.response.send_message("❌ Dice must have at least 2 sides!", ephemeral=True)
        result = random.randint(1, sides)
        embed = discord.Embed(title=f"🎲 Rolling a d{sides}...", description=f"You rolled a **{result}**!", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="meme", description="Get a random meme from Reddit")
    async def meme(self, interaction: discord.Interaction):
        await interaction.response.defer()
        subreddit = random.choice(["memes", "dankmemes", "me_irl", "wholesomememes"])
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"https://www.reddit.com/r/{subreddit}/random.json?limit=1",
                    headers={"User-Agent": "DiscordBot/1.0"}
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        post = data[0]['data']['children'][0]['data']
                        if post.get('over_18'):
                            return await interaction.followup.send("⚠️ Got an NSFW meme, try again!")
                        embed = discord.Embed(title=post['title'][:256], url=f"https://reddit.com{post['permalink']}", color=discord.Color.orange())
                        embed.set_image(url=post.get('url', ''))
                        embed.set_footer(text=f"👍 {post['ups']} | r/{subreddit}")
                        await interaction.followup.send(embed=embed)
                    else:
                        await interaction.followup.send("❌ Couldn't fetch a meme right now!")
        except Exception:
            await interaction.followup.send("❌ Reddit might be unavailable. Try again later!")

    @app_commands.command(name="roast", description="Roast a member (all in good fun!)")
    @app_commands.describe(member="The unlucky member to roast")
    async def roast(self, interaction: discord.Interaction, member: discord.Member):
        embed = discord.Embed(title=f"🔥 Roasting {member.display_name}!", description=random.choice(ROASTS), color=discord.Color.red())
        embed.set_footer(text="All in good fun! 😄")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="avatar", description="Get a user's avatar")
    @app_commands.describe(member="The member whose avatar to show")
    async def avatar(self, interaction: discord.Interaction, member: discord.Member = None):
        m = member or interaction.user
        embed = discord.Embed(title=f"🖼️ {m.display_name}'s Avatar", color=discord.Color.blurple())
        embed.set_image(url=m.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="choose", description="Choose between multiple options")
    @app_commands.describe(options="Options separated by commas (e.g. pizza, burger, sushi)")
    async def choose(self, interaction: discord.Interaction, options: str):
        choices = [c.strip() for c in options.split(',') if c.strip()]
        if len(choices) < 2:
            return await interaction.response.send_message("❌ Provide at least 2 options separated by commas!", ephemeral=True)
        embed = discord.Embed(title="🤔 I choose...", description=f"**{random.choice(choices)}**", color=discord.Color.purple())
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Fun(bot))
