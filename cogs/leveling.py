import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import math

DATA_FILE = "levels.json"
MAX_LEVEL = 10000

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            return {}
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self):
        with open(DATA_FILE, "w") as f:
            json.dump(self.data, f, indent=4)

    def get_title(self, guild_id, level):
        guild_id = str(guild_id)
        if guild_id in self.data and "custom_titles" in self.data[guild_id]:
            sorted_milestones = sorted([int(k) for k in self.data[guild_id]["custom_titles"].keys()], reverse=True)
            for milestone in sorted_milestones:
                if level >= milestone:
                    return self.data[guild_id]["custom_titles"][str(milestone)]

        if level >= 10000: return "👑 [ Singularity Overlord ]"
        if level >= 5000:  return "🧠 [ Mainframe Overlord ]"
        if level >= 1000:  return "💾 [ Data Warden ]"
        if level >= 100:   return "⚡ [ Netrunner Elite ]"
        return "🌱 [ Script Kiddie ]"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        if guild_id not in self.data:
            self.data[guild_id] = {"users": {}, "custom_titles": {}}
        if "users" not in self.data[guild_id]:
            self.data[guild_id]["users"] = {}

        if user_id not in self.data[guild_id]["users"]:
            self.data[guild_id]["users"][user_id] = {"xp": 0, "level": 0}

        user_profile = self.data[guild_id]["users"][user_id]
        if user_profile["level"] >= MAX_LEVEL:
            return

        user_profile["xp"] += 5
        current_xp = user_profile["xp"]
        current_lvl = user_profile["level"]
        next_lvl_xp = (current_lvl + 1) * 100

        while current_xp >= next_lvl_xp and current_lvl < MAX_LEVEL:
            current_xp -= next_lvl_xp
            current_lvl += 1
            next_lvl_xp = (current_lvl + 1) * 100
            user_profile["level"] = current_lvl
            user_profile["xp"] = current_xp

            try:
                await message.channel.send(f"⚡ **SYSTEM UPDATE** | {message.author.mention} has upgraded to **Level {current_lvl}**!")
            except discord.Forbidden:
                pass

        self.save_data()

    # --- Cool Framework /level Command ---
    @app_commands.command(name="level", description="Displays your current server level and rank profile.")
    async def level_command(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        xp = 0
        level = 0

        if guild_id in self.data and "users" in self.data[guild_id] and user_id in self.data[guild_id]["users"]:
            xp = self.data[guild_id]["users"][user_id]["xp"]
            level = self.data[guild_id]["users"][user_id]["level"]

        title = self.get_title(guild_id, level)
        
        # Progress Bar Math
        if level >= MAX_LEVEL:
            progress_bar = "██████████"
            xp_display = "MAX LEVEL"
        else:
            next_lvl_xp = (level + 1) * 100
            filled = math.floor((xp / next_lvl_xp) * 10)
            filled = max(0, min(10, filled))
            progress_bar = "█" * filled + "░" * (10 - filled)
            xp_display = f"{xp:,} / {next_lvl_xp:,} XP"

        # Framework Layout Output
        framework = (
            f"╔══════════════════════════════════╗\n"
            f"   👤 **USER DATA LINK:** {member.name.upper()}\n"
            f"╚══════════════════════════════════╝\n"
            f"> 🏆 **RANK STATUS:** `{title}`\n"
            f"> 📈 **NODE LEVEL:** `Lvl {level:,} / {MAX_LEVEL:,}`\n"
            f"> 📊 **SYNC PROGRESS:** `[{progress_bar}]` *({xp_display})*\n"
            f"────────────────────────────────────"
        )
        await interaction.response.send_message(framework)

    # Legacy profile command pointing to the exact same logic
    @app_commands.command(name="profile", description="Displays your server level status.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        await self.level_command(interaction, member)

    @app_commands.command(name="renamelevel", description="Sets a custom rank title for a level milestone.")
    @app_commands.default_permissions(manage_guild=True)
    async def rename_level(self, interaction: discord.Interaction, level: int, new_title: str):
        guild_id = str(interaction.guild.id)

        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message("❌ Error: Access denied.", ephemeral=True)
            return

        if level < 0 or level > MAX_LEVEL:
            await interaction.response.send_message(f"❌ Error: Level must be between 0 and {MAX_LEVEL}.", ephemeral=True)
            return

        if guild_id not in self.data:
            self.data[guild_id] = {"users": {}, "custom_titles": {}}
        if "custom_titles" not in self.data[guild_id]:
            self.data[guild_id]["custom_titles"] = {}

        self.data[guild_id]["custom_titles"][str(level)] = new_title
        self.save_data()

        await interaction.response.send_message(f"✅ Success! Level {level} milestone has been renamed to: **{new_title}**")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
