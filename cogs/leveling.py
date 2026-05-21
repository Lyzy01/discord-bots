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
        
        # Check if the guild has custom renamed titles stored in the JSON
        if guild_id in self.data and "custom_titles" in self.data[guild_id]:
            # Sort milestones in descending order to match the highest reached tier
            sorted_milestones = sorted(
                [int(k) for k in self.data[guild_id]["custom_titles"].keys()], 
                reverse=True
            )
            for milestone in sorted_milestones:
                if level >= milestone:
                    return self.data[guild_id]["custom_titles"][str(milestone)]

        # --- Fallback Default Terminal Titles ---
        if level >= 10000: return "👑 [ Level 10K: Singularity Overlord ]"
        if level >= 7500:  return "🌌 [ Level 7.5K: Cosmic Architect ]"
        if level >= 5000:  return "🧠 [ Level 5K: Mainframe Overlord ]"
        if level >= 2500:  return "🔮 [ Level 2.5K: Cyber Necromancer ]"
        if level >= 1000:  return "💾 [ Level 1K: Data Warden ]"
        if level >= 500:   return "🛡️ [ Level 500: System Vanguard ]"
        if level >= 100:   return "⚡ [ Level 100: Netrunner Elite ]"
        if level >= 50:    return "💻 [ Level 50: Root Admin ]"
        if level >= 20:    return "🛠️ [ Level 20: Elite Dev ]"
        if level >= 5:     return "📝 [ Level 5: Novice Coder ]"
        return "🌱 [ Level 0: Script Kiddie ]"

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        if guild_id not in self.data:
            self.data[guild_id] = {}

        if "users" not in self.data[guild_id]:
            # Move existing users nesting if upgrading from previous json format
            if user_id in self.data[guild_id] or len(self.data[guild_id]) == 0:
                old_data = self.data[guild_id].copy()
                self.data[guild_id] = {"users": old_data, "custom_titles": {}}
            else:
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

        if user_profile["level"] >= MAX_LEVEL:
            user_profile["level"] = MAX_LEVEL
            user_profile["xp"] = 0

        self.save_data()

    @app_commands.command(name="profile", description="Displays your server level and terminal network status.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        guild_id = str(interaction.guild.id)
        user_id = str(member.id)

        xp = 0
        level = 0

        if guild_id in self.data and "users" in self.data[guild_id] and user_id in self.data[guild_id]["users"]:
            xp = self.data[guild_id]["users"][user_id]["xp"]
            level = self.data[guild_id]["users"][user_id]["level"]

        title = self.get_title(guild_id, level)
        
        if level >= MAX_LEVEL:
            progress_bar = "██████████"
            xp_display = "MAX LEVEL REACHED"
        else:
            next_lvl_xp = (level + 1) * 100
            progress_segments = 10
            filled_segments = math.floor((xp / next_lvl_xp) * progress_segments)
            filled_segments = max(0, min(progress_segments, filled_segments))
            progress_bar = "█" * filled_segments + "░" * (progress_segments - filled_segments)
            xp_display = f"{xp}/{next_lvl_xp} XP"

        terminal_card = (
            f"```ansi\n"
            f"\u001b[1;36m[ TERMINAL ID: {member.name.upper()} ]\u001b[0m\n"
            f"----------------------------------------\n"
            f"» STATUS:     {title}\n"
            f"» NODE LEVEL: {level:,} / {MAX_LEVEL:,}\n"
            f"» DATA SYNC:  [{progress_bar}] {xp_display}\n"
            f"----------------------------------------\n"
            f"```"
        )

        await interaction.response.send_message(terminal_card)

    @app_commands.command(name="renamelevel", description="Sets a custom rank title for a specific level milestone.")
    @app_commands.default_permissions(manage_guild=True)
    async def rename_level(self, interaction: discord.Interaction, level: int, new_title: str):
        guild_id = str(interaction.guild.id)

        # Higher ranks permission check fallback (Manage Server or Guild Owner)
        if not interaction.user.guild_permissions.manage_guild and interaction.user.id != interaction.guild.owner_id:
            await interaction.response.send_message(
                "
http://googleusercontent.com/immersive_entry_chip/0

### What changed?
1. **The `/renamelevel` Command:** Added with arguments for `level` (e.g., `5`) and `new_title` (e.g., `⚙️ [ Level 5: System Intern ]`).
2. **Strict Admin Restriction:** Protected by both Discord's app command middleware (`@app_commands.default_permissions`) and an explicit back-end check verifying that only the Server Owner or Admins with **Manage Server** rights can write to the JSON file.
3. **Structured Database Integration:** The `levels.json` file splits user progression points and server configuration parameters cleanly into separate structures (`users` and `custom_titles`) to avoid conflicts.
