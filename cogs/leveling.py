import discord
from discord.ext import commands
from discord import app_commands
import json
import os
import math

DATA_FILE = "/data/levels.json"
MAX_LEVEL = 10000

class Leveling(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.data = self.load_data()

    def load_data(self):
        if not os.path.exists(DATA_FILE):
            # Fallback check for local vs disk volume setup
            if os.path.exists("levels.json"):
                with open("levels.json", "r") as f:
                    try: return json.load(f)
                    except: return {}
            return {}
        with open(DATA_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {}

    def save_data(self):
        # Ensure the directory exists before saving
        os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
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

    async def check_and_assign_role(self, member, level):
        guild = member.guild
        guild_id = str(guild.id)
        
        milestones = [1, 5, 10, 20, 30, 40, 50, 100, 500, 1000]
        if level not in milestones:
            return

        role_name = f"Level {level}+"
        role = discord.utils.get(guild.roles, name=role_name)
        
        # Safe default color conversion
        chosen_color = discord.Color.from_rgb(max(50, 255 - (level * 2)), min(200, 50 + (level * 2)), 230)
        
        if guild_id in self.data and "role_colors" in self.data[guild_id]:
            hex_str = self.data[guild_id]["role_colors"].get(str(level))
            if hex_str:
                try:
                    if not hex_str.startswith("#"):
                        hex_str = f"#{hex_str}"
                    chosen_color = discord.Color.from_str(hex_str)
                except ValueError:
                    pass

        if role is None:
            try:
                role = await guild.create_role(
                    name=role_name, 
                    color=chosen_color, 
                    reason="Automated Leveling Milestone System"
                )
            except discord.Forbidden:
                print(f"❌ Missing permissions to create: {role_name}")
                return

        if role and role not in member.roles:
            try:
                await member.add_roles(role)
            except discord.Forbidden:
                print(f"❌ Cannot assign role {role_name}.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.guild is None:
            return

        guild_id = str(message.guild.id)
        user_id = str(message.author.id)

        if guild_id not in self.data:
            self.data[guild_id] = {"users": {}, "custom_titles": {}, "role_colors": {}}
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

            await self.check_and_assign_role(message.author, current_lvl)

            try:
                await message.channel.send(f"⚡ **SYSTEM UPDATE** | {message.author.mention} has upgraded to **Level {current_lvl}**!")
            except discord.Forbidden:
                pass

        self.save_data()

    async def generate_level_embed(self, interaction: discord.Interaction, member: discord.Member):
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
            xp_display = "MAX STATUS ACHIEVEMENT"
        else:
            next_lvl_xp = (level + 1) * 100
            filled = math.floor((xp / next_lvl_xp) * 10)
            filled = max(0, min(10, filled))
            progress_bar = "█" * filled + "░" * (10 - filled)
            xp_display = f"{xp:,} / {next_lvl_xp:,} XP"

        embed = discord.Embed(
            title=f"👤 {member.display_name}'s Progress Core",
            color=discord.Color.purple()
        )
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="🏆 Current Title Rank", value=f"`{title}`", inline=False)
        embed.add_field(name="📈 Node Level Status", value=f"**Level {level:,}** / `{MAX_LEVEL:,}`", inline=True)
        embed.add_field(name="📊 Sync Progress Bar", value=f"`[{progress_bar}]` \n*{xp_display}*", inline=False)
        embed.set_footer(text=f"Server Identity Index: {interaction.guild.name}")
        
        return embed

    @app_commands.command(name="level", description="Displays your current server level and rank profile.")
    async def level_command(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = await self.generate_level_embed(interaction, member)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="profile", description="Displays your server profile status.")
    async def profile(self, interaction: discord.Interaction, member: discord.Member = None):
        member = member or interaction.user
        embed = await self.generate_level_embed(interaction, member)
        await interaction.response.send_message(embed=embed)

    # --- CRASH FIXED COLOR COMMAND ---
    @app_commands.command(name="setrolecolor", description="Changes the color of an existing level milestone role.")
    @app_commands.describe(level="The level milestone (e.g., 1, 5, 10)", hex_color="The Hex color code (e.g., #FF5555 or 00FFCC)")
    @app_commands.default_permissions(manage_roles=True)
    async def set_role_color(self, interaction: discord.Interaction, level: int, hex_color: str):
        guild = interaction.guild
        guild_id = str(guild.id)

        # Make sure hex string formatting satisfies format requirements
        formatted_hex = hex_color if hex_color.startswith("#") else f"#{hex_color}"
        try:
            resolved_color = discord.Color.from_str(formatted_hex)
        except ValueError:
            await interaction.response.send_message("❌ Error: Invalid Hex code format. Use formats like `#FF5555` or `00FFCC`.", ephemeral=True)
            return

        if guild_id not in self.data:
            self.data[guild_id] = {"users": {}, "custom_titles": {}, "role_colors": {}}
        if "role_colors" not in self.data[guild_id]:
            self.data[guild_id]["role_colors"] = {}

        self.data[guild_id]["role_colors"][str(level)] = formatted_hex
        self.save_data()

        target_role_name = f"Level {level}+"
        existing_role = discord.utils.get(guild.roles, name=target_role_name)
        
        if existing_role:
            try:
                await existing_role.edit(color=resolved_color, reason=f"Color modified via /setrolecolor by {interaction.user}")
                await interaction.response.send_message(f"✅ Modified color for **{target_role_name}** to `{formatted_hex}` successfully across the server!")
            except discord.Forbidden:
                await interaction.response.send_message("❌ Error: Bot position hierarchy is lower than the target level role. Drag the bot's role higher in Server Settings!", ephemeral=True)
        else:
            await interaction.response.send_message(f"💾 Saved configuration! Next time a user updates to **Level {level}**, their new role will spawn with `{formatted_hex}`.")

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
            self.data[guild_id] = {"users": {}, "custom_titles": {}, "role_colors": {}}
        if "custom_titles" not in self.data[guild_id]:
            self.data[guild_id]["custom_titles"] = {}

        self.data[guild_id]["custom_titles"][str(level)] = new_title
        self.save_data()

        await interaction.response.send_message(f"✅ Success! Level {level} milestone has been renamed to: **{new_title}**")

async def setup(bot):
    await bot.add_cog(Leveling(bot))
