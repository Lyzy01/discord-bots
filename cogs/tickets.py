import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import io
import os
from datetime import datetime

# DO NOT REMOVE THIS - Needed for your web metrics
try:
    import keep_alive
except ImportError:
    keep_alive = None

OWNER_USERNAME = "kimmendez01"
OWNER_DISCORD_ID = 1366110873248071801  

processed_cases_counter = 0

def is_authorized_staff(interaction: discord.Interaction) -> bool:
    if interaction.user.id == OWNER_DISCORD_ID or interaction.user.name == OWNER_USERNAME:
        return True
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    return any(any(k in role.name.lower() for k in admin_keywords) for role in interaction.user.roles)

def is_ticket_channel(channel_name: str) -> bool:
    name_lower = channel_name.lower()
    return "incident-" in name_lower or "appeal-" in name_lower or "review-" in name_lower

async def send_audit_archive(guild: discord.Guild, title: str, user_id: int, fields: dict, decision: str, staff: discord.User):
    log_channel = discord.utils.get(guild.text_channels, name="staff-audit-logs")
    if not log_channel:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            log_channel = await guild.create_text_channel(name="staff-audit-logs", overwrites=overwrites)
        except:
            return

    color = discord.Color.green() if decision == "APPROVED" else (discord.Color.red() if decision == "DENIED" else discord.Color.greyple())
    audit_embed = discord.Embed(title=f"📋 Archive Record: {title}", color=color)
    audit_embed.add_field(name="👤 Original Submitter", value=f"<@{user_id}>", inline=False)
    for name, val in fields.items():
        audit_embed.add_field(name=name, value=val, inline=False)
    audit_embed.add_field(name="⚡ Resolution", value=f"**{decision}**", inline=True)
    audit_embed.add_field(name="🛠️ Staff", value=staff.mention, inline=True)
    await log_channel.send(embed=audit_embed)

class StaffControlPanel(discord.ui.View):
    def __init__(self, target_user_id: int = None, ticket_type: str = None, raw_fields: dict = None):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id
        self.ticket_type = ticket_type
        self.raw_fields = raw_fields

    def parse_embed_data(self, interaction: discord.Interaction):
        if self.target_user_id and self.ticket_type: return True
        try:
            embed = interaction.message.embeds[0]
            self.ticket_type = "Incident" if "Incident" in embed.title else "Review"
            self.raw_fields = {f.name: f.value for f in embed.fields}
            if embed.footer and "ID:" in embed.footer.text:
                self.target_user_id = int(embed.footer.text.split("ID:")[-1].strip())
            return True
        except: return False

    @discord.ui.button(label="✅ Approve", style=discord.ButtonStyle.success, custom_id="panel_approve")
    async def approve(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction): return
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        if self.target_user_id:
            try:
                u = await interaction.client.fetch_user(self.target_user_id)
                await u.send(f"✅ Your {self.ticket_type} has been **APPROVED**.")
            except: pass
        await send_audit_archive(interaction.guild, f"{self.ticket_type} Approval", self.target_user_id, self.raw_fields, "APPROVED", interaction.user)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Deny", style=discord.ButtonStyle.danger, custom_id="panel_deny")
    async def deny(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction): return
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        if self.target_user_id:
            try:
                u = await interaction.client.fetch_user(self.target_user_id)
                await u.send(f"❌ Your {self.ticket_type} has been **DENIED**.")
            except: pass
        await send_audit_archive(interaction.guild, f"{self.ticket_type} Rejection", self.target_user_id, self.raw_fields, "DENIED", interaction.user)
        await interaction.channel.delete()

class BugReportModal(discord.ui.Modal, title="Report Bugs & Errors"):
    bug_title = discord.ui.TextInput(label="Feature Affected", placeholder="e.g. /ai", required=True)
    details = discord.ui.TextInput(label="Details", style=discord.TextStyle.paragraph, required=True)
    feedback = discord.ui.TextInput(label="Feedback (Optional)", style=discord.TextStyle.paragraph, required=False)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🐛 Bug Report", color=discord.Color.red())
        embed.add_field(name="Target", value=self.bug_title.value)
        embed.add_field(name="Log", value=self.details.value)
        embed.set_footer(text=f"From: {interaction.user.name} | ID: {interaction.user.id}")
        owner = await interaction.client.fetch_user(OWNER_DISCORD_ID)
        await owner.send(embed=embed)
        await interaction.followup.send("✅ Sent to developer!", ephemeral=True)

class PlayerReportModal(discord.ui.Modal, title="Submit Incident Report"):
    username = discord.ui.TextInput(label="Target Player", required=True)
    reason = discord.ui.TextInput(label="Details", style=discord.TextStyle.paragraph, required=True)
    evidence = discord.ui.TextInput(label="Proof Link", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        overwrites = {interaction.guild.default_role: discord.PermissionOverwrite(read_messages=False), interaction.user: discord.PermissionOverwrite(read_messages=True)}
        channel = await interaction.guild.create_text_channel(name=f"incident-{interaction.user.name}", overwrites=overwrites)
        embed = discord.Embed(title="🛡️ Incident Logged", color=discord.Color.orange())
        embed.add_field(name="Player", value=self.username.value)
        embed.add_field(name="Reason", value=self.reason.value)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        await channel.send(embed=embed, view=StaffControlPanel(target_user_id=interaction.user.id, ticket_type="Incident"))
        await interaction.followup.send(f"✅ Opened: {channel.mention}", ephemeral=True)

class ReportButtonView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="File Incident Report 🚩", style=discord.ButtonStyle.danger, custom_id="trig_rep")
    async def click(self, interaction, button): await interaction.response.send_modal(PlayerReportModal())

class AppealButtonView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Request Case Review 📑", style=discord.ButtonStyle.primary, custom_id="trig_app")
    async def click(self, interaction, button): await interaction.followup.send("Appeal logic here", ephemeral=True)

class GeneralBugDeployView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Report Bot Bugs 🐛", style=discord.ButtonStyle.secondary, custom_id="trig_bug")
    async def click(self, interaction, button): await interaction.response.send_modal(BugReportModal())

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        self.update_web_metrics.start()

    @tasks.loop(seconds=10)
    async def update_web_metrics(self):
        if not self.bot.is_ready() or not keep_alive: return
        keep_alive.LIVE_STATS["servers"] = len(self.bot.guilds)
        keep_alive.LIVE_STATS["processed"] = processed_cases_counter

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReportButtonView())
        self.bot.add_view(AppealButtonView())
        self.bot.add_view(StaffControlPanel())
        self.bot.add_view(GeneralBugDeployView())

    @app_commands.command(name="claim", description="Assign ticket")
    async def claim(self, interaction: discord.Interaction):
        if not is_authorized_staff(interaction): return
        await interaction.response.send_message(f"🔒 Claimed by {interaction.user.mention}")

    @app_commands.command(name="adduiplayerreport", description="Deploy report UI")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_authorized_staff(interaction): return
        await channel.send(embed=discord.Embed(title="🛡️ Integrity Center", color=discord.Color.red()), view=ReportButtonView())
        await interaction.response.send_message("✅ Deployed", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
