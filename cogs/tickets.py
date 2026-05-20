import discord
from discord import app_commands
from discord.ext import commands

OWNER_USERNAME = "kimmendez01"

# =================================================================
# 1. THE CANCEL / CLOSE TICKET BUTTON
# =================================================================
class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # Keeps button active permanently

    @discord.ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.secondary, custom_id="close_ticket_button")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        # Admin/Staff security check
        admin_keywords = ["admin", "moderator", "staff", "owner"]
        is_staff = any(any(k in role.name.lower() for k in admin_keywords) for role in interaction.user.roles)
        
        # Allow the button to work if it's the owner or any staff member
        if interaction.user.name == OWNER_USERNAME or is_staff:
            await interaction.response.send_message("⚙️ *Closing ticket and deleting this temporary channel in 5 seconds...*")
            import asyncio
            await asyncio.sleep(5)
            await interaction.channel.delete()
        else:
            await interaction.response.send_message("❌ Only administrators or moderators can close this ticket room.", ephemeral=True)

# =================================================================
# 2. THE POP-UP FORMS (MODALS)
# =================================================================
class PlayerReportModal(discord.ui.Modal, title="Player Report"):
    username = discord.ui.TextInput(
        label="Username", 
        placeholder="Username of the user you are reporting", 
        required=True
    )
    reason = discord.ui.TextInput(
        label="Why are you reporting this user?", 
        style=discord.TextStyle.paragraph,
        placeholder="Please try and provide context - don't just say 'Exploiting'", 
        required=True
    )
    evidence = discord.ui.TextInput(
        label="Evidence", 
        style=discord.TextStyle.paragraph,
        placeholder="Video evidence of the user breaking the rules", 
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        # Dynamic Permission System: Hide room from standard users
        admin_keywords = ["admin", "moderator", "staff", "owner"]
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        
        # Grant automatic access to any Admin/Mod roles
        for role in guild.roles:
            if any(k in role.name.lower() for k in admin_keywords):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Create the temporary room
        channel = await guild.create_text_channel(name=f"report-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="🚨 New In-Game Player Report Submitted", color=discord.Color.dark_red())
        embed.add_field(name="👤 Target Offender", value=self.username.value, inline=False)
        embed.add_field(name="📝 Violation Context", value=self.reason.value, inline=False)
        embed.add_field(name="🎬 Provided Evidence Link/Data", value=self.evidence.value, inline=False)
        embed.set_footer(text=f"Filed by: {interaction.user.name} ({interaction.user.id})")
        
        # Send details alongside the administrative closing button view
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Report logged! Private room spawned: {channel.mention}", ephemeral=True)


class BanAppealModal(discord.ui.Modal, title="Ban Appeal"):
    username = discord.ui.TextInput(
        label="Your Roblox Username", 
        placeholder="Username of the account you are appealing for", 
        required=True
    )
    reason = discord.ui.TextInput(
        label="Appeal Reason", 
        style=discord.TextStyle.paragraph,
        placeholder="Why do you believe you were banned incorrectly?", 
        required=True
    )

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        admin_keywords = ["admin", "moderator", "staff", "owner"]
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role in guild.roles:
            if any(k in role.name.lower() for k in admin_keywords):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        # Create the temporary room
        channel = await guild.create_text_channel(name=f"appeal-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="⚖️ Roblox Restriction Appeal Filed", color=discord.Color.blue())
        embed.add_field(name="👤 Roblox Username", value=self.username.value, inline=True)
        embed.add_field(name="🆔 Discord Target", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Case Argument Details", value=self.reason.value, inline=False)
        embed.set_footer(text="Awaiting High-Tier Admin Evaluation Panel...")
        
        # Send details alongside the administrative closing button view
        await channel.send(embed=embed, view=CloseTicketView())
        await interaction.followup.send(f"✅ Appeal logged! Private room spawned: {channel.mention}", ephemeral=True)

# =================================================================
# 3. THE SETUP BASE BOARDS
# =================================================================
class ReportButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Report User", style=discord.ButtonStyle.danger, custom_id="trigger_player_report")
    async def click_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerReportModal())

class AppealButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Appeal Ban", style=discord.ButtonStyle.danger, custom_id="trigger_ban_appeal")
    async def click_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanAppealModal())


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="adduiplayerreport", description="Deploy the player report interface to a chosen channel")
    @app_commands.describe(channel="The channel where the embed board should be placed")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🎮 Submit In-Game Reports",
            description=(
                "If you spotted a player breaking community guidelines or exploiting inside the game, click the button below to alert our staff team.\n\n"
                "**Requirements:**\n"
                "• Target account name must be provided accurately.\n"
                "• Legitimate video/screenshot links must be included for fast actions."
            ),
            color=discord.Color.red()
        )
        embed.set_footer(text="Ly's Automated Moderation Core")
        
        await channel.send(embed=embed, view=ReportButtonView())
        await interaction.followup.send(f"✅ Interface dropped safely inside {channel.mention}!", ephemeral=True)

    @app_commands.command(name="adduiappealban", description="Deploy the ban appeal interface to a chosen channel")
    @app_commands.describe(channel="The channel where the embed board should be placed")
    async def add_ui_appeal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="Appeal Your Ban",
            description=(
                "If you believe you were banned **unfairly**, you can appeal your ban by clicking the button below.\n\n"
                "**You MUST include the following details in your appeal or it will be dismissed:**\n"
                "• Your Roblox username\n"
                "• Why you believe you were banned unfairly\n"
                "• Any evidence you have to support your claim\n\n"
                "**NOTE:**\n"
                "• Exploiting is a **PERMANENT** ban. We do not offer second chances to anyone if they are banned for exploiting.\n"
                "• If you were banned more than **30 days ago**, your appeal will be denied. This rule has absolutely **NO EXCEPTIONS**.\n\n"
                "Appeals take time to process, so please refrain from pinging staff members or submitting multiple appeals."
            ),
            color=discord.Color.from_rgb(43, 45, 49)
        )
        
        await channel.send(embed=embed, view=AppealButtonView())
        await interaction.followup.send(f"✅ Interface dropped safely inside {channel.mention}!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
