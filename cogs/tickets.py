import discord
from discord import app_commands
from discord.ext import commands
import asyncio

OWNER_USERNAME = "kimmendez01"

# Helper function to check if the interacting user is an eligible administrator/staff member
def is_authorized_staff(interaction: discord.Interaction) -> bool:
    if interaction.user.name == OWNER_USERNAME:
        return True
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    return any(any(k in role.name.lower() for k in admin_keywords) for role in interaction.user.roles)

# =================================================================
# 1. THE STAFF EVALUATION CONTROL PANEL (BUTTONS PANEL)
# =================================================================
class StaffControlPanel(discord.ui.View):
    def __init__(self, target_user: discord.User, ticket_type: str):
        super().__init__(timeout=None)
        self.target_user = target_user
        self.ticket_type = ticket_type # "Incident" or "Review"

    @discord.ui.button(label="✅ Approve Case", style=discord.ButtonStyle.success, custom_id="panel_approve_case")
    async def approve_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied. Only high-ranking operators can evaluate this case.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Processing approval authorization...*")
        
        # Determine specific DM text layout based on the file category
        if self.ticket_type == "Incident":
            msg_content = "🛡️ **Ly's Security Operations Notice:** Your recently filed incident report has been thoroughly investigated and **APPROVED** by our team. Action has been taken against the target offender. Thank you for helping keep our community clean!"
        else:
            msg_content = "⚖️ **Ly's Review Desk Notice:** Excellent news! Your enforcement appeal has been formally **APPROVED** upon review. Your account status and access permissions are being restored immediately."

        # Attempt to DM the user
        try:
            await self.target_user.send(msg_content)
        except discord.Forbidden:
            print(f"Could not DM user {self.target_user.id} - DMs locked down.")

        await asyncio.sleep(2)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Deny Case", style=discord.ButtonStyle.danger, custom_id="panel_deny_case")
    async def deny_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied. Only high-ranking operators can evaluate this case.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Processing denial authorization...*")
        
        if self.ticket_type == "Incident":
            msg_content = "🛡️ **Ly's Security Operations Notice:** Your incident report submission has been reviewed and **DENIED**. The provided context or verification data was deemed insufficient to authorize disciplinary actions."
        else:
            msg_content = "⚖️ **Ly's Review Desk Notice:** Your enforcement appeal has been reviewed and **DENIED**. The restriction penalty against your account remains absolute as per our core server bylaws."

        try:
            await self.target_user.send(msg_content)
        except discord.Forbidden:
            print(f"Could not DM user {self.target_user.id} - DMs locked down.")

        await asyncio.sleep(2)
        await interaction.channel.delete()

    @discord.ui.button(label="🔒 Cancel Session", style=discord.ButtonStyle.secondary, custom_id="panel_cancel_session")
    async def cancel_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied. Only high-ranking operators can terminate this corridor.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Session termination authorized. Deleting data corridor instantly...*")
        await asyncio.sleep(3)
        await interaction.channel.delete()

# =================================================================
# 2. THE POP-UP FORMS (MODALS)
# =================================================================
class PlayerReportModal(discord.ui.Modal, title="Submit Incident Report"):
    username = discord.ui.TextInput(
        label="Target Player Account", 
        placeholder="Exact username of the rule-breaker", 
        required=True
    )
    reason = discord.ui.TextInput(
        label="Incident Context & Details", 
        style=discord.TextStyle.paragraph,
        placeholder="Explain exactly what happened (e.g., glitching, bad behavior). Avoid vague answers.", 
        required=True
    )
    evidence = discord.ui.TextInput(
        label="Proof / Media Evidence Link", 
        style=discord.TextStyle.paragraph,
        placeholder="Paste links to your video or screenshot clips here", 
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

        channel = await guild.create_text_channel(name=f"incident-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="🛡️ Security Core: Live Incident Logged", color=discord.Color.dark_orange())
        embed.add_field(name="👤 Flagged Account", value=f"`{self.username.value}`", inline=False)
        embed.add_field(name="📝 Situation Report", value=self.reason.value, inline=False)
        embed.add_field(name="🔗 Attached Verification", value=self.evidence.value, inline=False)
        embed.set_footer(text=f"Dispatched by: {interaction.user.name} • Evaluation Panel Ready Below")
        
        # Drop the panel inside the corridor and link it to the user who reported
        await channel.send(embed=embed, view=StaffControlPanel(target_user=interaction.user, ticket_type="Incident"))
        await interaction.followup.send(f"✅ Case registered successfully! Secure channel opened: {channel.mention}", ephemeral=True)


class BanAppealModal(discord.ui.Modal, title="Review Request System"):
    username = discord.ui.TextInput(
        label="Your In-Game Username", 
        placeholder="The account name that was restricted", 
        required=True
    )
    reason = discord.ui.TextInput(
        label="Case Argument / Defense Statement", 
        style=discord.TextStyle.paragraph,
        placeholder="Explain carefully why this restriction should be lifted or modified.", 
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

        channel = await guild.create_text_channel(name=f"review-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="⚖️ Enforcement Review Docket Initiated", color=discord.Color.teal())
        embed.add_field(name="👤 Restricted Account", value=f"`{self.username.value}`", inline=True)
        embed.add_field(name="🆔 Discord Contact", value=interaction.user.mention, inline=True)
        embed.add_field(name="📝 Defense Arguments", value=self.reason.value, inline=False)
        embed.set_footer(text="Awaiting review panel decision...")
        
        # Drop the panel inside the corridor and link it to the user who appealed
        await channel.send(embed=embed, view=StaffControlPanel(target_user=interaction.user, ticket_type="Review"))
        await interaction.followup.send(f"✅ Review request sent! Data room opened: {channel.mention}", ephemeral=True)

# =================================================================
# 3. THE MAIN INTERACTIVE DASHBOARD BOARDS
# =================================================================
class ReportButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="File Incident Report 🚩", style=discord.ButtonStyle.danger, custom_id="trigger_player_report")
    async def click_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerReportModal())

class AppealButtonView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Request Case Review 📑", style=discord.ButtonStyle.primary, custom_id="trigger_ban_appeal")
    async def click_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanAppealModal())


class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="adduiplayerreport", description="Deploy the custom incident reporting layout center")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🛡️ Integrity Operations Center",
            description=(
                "See someone breaking our core guidelines or using illegal exploits? Help keep our game safe.\n\n"
                "**Submission Guidelines:**\n"
                "• Provide the exact target profile name.\n"
                "• Include direct media links (clips/screencaps) showing the violation.\n\n"
                "Click the dispatch button below to securely brief our staff agents."
            ),
            color=discord.Color.dark_red()
        )
        embed.set_footer(text="Ly's Automated Moderation Core • Secure Line")
        
        await channel.send(embed=embed, view=ReportButtonView())
        await interaction.followup.send(f"✅ Security interface deployed in {channel.mention}!", ephemeral=True)

    @app_commands.command(name="adduiappealban", description="Deploy the custom account restriction appeal desk")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_appeal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="⚖️ Enforcement Appeal Operations",
            description=(
                "If an administrative action was taken against your account and you believe it was done in error, you may present your arguments below.\n\n"
                "**Review Protocols (Must Follow):**\n"
                "• State your accurate in-game username.\n"
                "• Detail exactly why the restriction should be reversed or mitigated.\n"
                "• Supply any critical context or validation material to aid your case.\n\n"
                "**CRITICAL SECURITY RULES:**\n"
                "• Exploiting infractions are designated as **NON-NEGOTIABLE** and will not receive second-chance overrides.\n"
                "• Restrictions older than **30 days** are archived and permanently locked from future evaluations.\n\n"
                "*Every submission creates a private corridor directly with high staff. Please do not ping personnel after opening.*"
            ),
            color=discord.Color.from_rgb(32, 34, 37)
        )
        embed.set_footer(text="Ly's Automated Review Systems • Legal Core")
        
        await channel.send(embed=embed, view=AppealButtonView())
        await interaction.followup.send(f"✅ Appeal interface deployed in {channel.mention}!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
