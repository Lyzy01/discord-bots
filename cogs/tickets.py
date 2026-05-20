import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from groq import Groq
import os
import keep_alive

OWNER_USERNAME = "kimmendez01"

# Counter to log processed files globally across memory resets
processed_cases_counter = 0

def is_authorized_staff(interaction: discord.Interaction) -> bool:
    if interaction.user.name == OWNER_USERNAME:
        return True
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    return any(any(k in role.name.lower() for k in admin_keywords) for role in interaction.user.roles)

# =================================================================
# ADVANCED AUDIT LOG ARCHIVER FUNCTION
# =================================================================
async def send_audit_archive(guild: discord.Guild, title: str, user: discord.User, fields: dict, decision: str, staff: discord.User):
    """Locates or builds a permanent logging audit text channel and records a receipt."""
    log_channel = discord.utils.get(guild.text_channels, name="staff-audit-logs")
    
    if not log_channel:
        try:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True)
            }
            log_channel = await guild.create_text_channel(name="staff-audit-logs", overwrites=overwrites)
            await log_channel.send("📁 **System Registry: Audit Logs Corridor Initialized Securely.**")
        except Exception as e:
            print(f"Failed to auto-spawn log vault channel: {e}")
            return

    color = discord.Color.green() if decision == "APPROVED" else (discord.Color.red() if decision == "DENIED" else discord.Color.greyple())

    audit_embed = discord.Embed(title=f"📋 Archive Record: {title}", color=color)
    audit_embed.add_field(name="👤 Original Submitter", value=f"{user.mention} (`{user.id}`)", inline=False)
    
    for name, val in fields.items():
        audit_embed.add_field(name=name, value=val, inline=False)
        
    audit_embed.add_field(name="⚡ Resolution Action", value=f"**{decision}**", inline=True)
    audit_embed.add_field(name="🛠️ Handling Evaluator", value=staff.mention, inline=True)
    audit_embed.set_footer(text="Ly's Permanent Security Vault Database")

    try:
        await log_channel.send(embed=audit_embed)
    except Exception as e:
        print(f"Failed to post receipt into audit vault: {e}")

# =================================================================
# THE THREE-BUTTON STAFF CONTROL PANEL
# =================================================================
class StaffControlPanel(discord.ui.View):
    def __init__(self, target_user: discord.User, ticket_type: str, raw_fields: dict):
        super().__init__(timeout=None)
        self.target_user = target_user
        self.ticket_type = ticket_type
        self.raw_fields = raw_fields

    @discord.ui.button(label="✅ Approve Case", style=discord.ButtonStyle.success, custom_id="panel_approve_case")
    async def approve_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        global processed_cases_counter
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Processing case approval actions...*")
        processed_cases_counter += 1
        
        if self.ticket_type == "Incident":
            msg = "🛡️ **Ly's Security Operations Notice:** Your recently filed incident report has been thoroughly investigated and **APPROVED** by our team. Action has been taken against the target offender."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Excellent news! Your enforcement appeal has been formally **APPROVED** upon review. Your account status is being restored."

        try: await self.target_user.send(msg)
        except discord.Forbidden: pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Approval", self.target_user, self.raw_fields, "APPROVED", interaction.user)
        
        await asyncio.sleep(2)
        await interaction.channel.delete()

    @discord.ui.button(label="❌ Deny Case", style=discord.ButtonStyle.danger, custom_id="panel_deny_case")
    async def deny_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        global processed_cases_counter
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Processing case denial actions...*")
        processed_cases_counter += 1
        
        if self.ticket_type == "Incident":
            msg = "🛡️ **Ly's Security Operations Notice:** Your incident report submission has been reviewed and **DENIED**. Context or verification data was insufficient."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Your enforcement appeal has been reviewed and **DENIED**. The restriction penalty remains absolute."

        try: await self.target_user.send(msg)
        except discord.Forbidden: pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Rejection", self.target_user, self.raw_fields, "DENIED", interaction.user)

        await asyncio.sleep(2)
        await interaction.channel.delete()

    @discord.ui.button(label="🔒 Cancel Session", style=discord.ButtonStyle.secondary, custom_id="panel_cancel_session")
    async def cancel_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied.", ephemeral=True)
        
        await interaction.response.send_message("⚙️ *Terminating data corridor instantly...*")
        await send_audit_archive(interaction.guild, f"{self.ticket_type} Wiped", self.target_user, self.raw_fields, "TERMINATED/CANCELLED", interaction.user)
        await asyncio.sleep(2)
        await interaction.channel.delete()

# =================================================================
# THE POP-UP FORMS (MODALS) WITH ASYNCHRONOUS GROQ AI TRIAGING CORES
# =================================================================
class PlayerReportModal(discord.ui.Modal, title="Submit Incident Report"):
    username = discord.ui.TextInput(label="Target Player Account", placeholder="Username of the rule-breaker", required=True)
    reason = discord.ui.TextInput(label="Incident Context & Details", style=discord.TextStyle.paragraph, placeholder="Explain carefully what happened...", required=True)
    evidence = discord.ui.TextInput(label="Proof / Media Evidence Link", style=discord.TextStyle.paragraph, placeholder="Paste links to verification content here", required=True)

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
        embed.add_field(name="🤖 Core AI Pre-Screen Evaluation", value="⏳ *Analyzing report context via Groq AI cluster framework...*", inline=False)
        embed.set_footer(text=f"Dispatched by: {interaction.user.name}")
        
        saved_fields = {"Target Player": self.username.value, "Report Details": self.reason.value, "Media Links": self.evidence.value}
        
        panel_msg = await channel.send(embed=embed, view=StaffControlPanel(target_user=interaction.user, ticket_type="Incident", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Case registered! Secure channel opened: {channel.mention}", ephemeral=True)

        # Offload the slow Groq API generation request asynchronously
        async def fetch_ai_assessment():
            try:
                loop = asyncio.get_event_loop()
                def call_groq():
                    # Pulls GROQ_API_KEY from your Render dashboard settings
                    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                    ai_prompt = (
                        f"You are a professional game server moderation scanner. Review this report:\n"
                        f"Target: {self.username.value}\nReason: {self.reason.value}\nEvidence Link: {self.evidence.value}\n"
                        f"Give a short 2-sentence feedback label summary telling staff if it seems real, missing clear facts, or potentially spam."
                    )
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.5,
                        max_tokens=150
                    )
                    return completion.choices[0].message.content
                
                ai_assessment = await loop.run_in_executor(None, call_groq)
            except Exception as e:
                ai_assessment = f"⚠️ *AI triage processing error: {e}*"

            embed.set_field_at(3, name="🤖 Core AI Pre-Screen Evaluation", value=f"*{ai_assessment}*", inline=False)
            await panel_msg.edit(embed=embed)

        asyncio.create_task(fetch_ai_assessment())


class BanAppealModal(discord.ui.Modal, title="Review Request System"):
    username = discord.ui.TextInput(label="Your In-Game Username", placeholder="The account name that was restricted", required=True)
    reason = discord.ui.TextInput(label="Case Argument / Defense Statement", style=discord.TextStyle.paragraph, placeholder="Explain carefully why you should be unbanned...", required=True)

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
        embed.add_field(name="🤖 Core AI Pre-Screen Evaluation", value="⏳ *Analyzing defense context via Groq AI cluster framework...*", inline=False)
        embed.set_footer(text="Awaiting review panel decision...")
        
        saved_fields = {"Account Username": self.username.value, "Defense Reasons Given": self.reason.value}
        
        panel_msg = await channel.send(embed=embed, view=StaffControlPanel(target_user=interaction.user, ticket_type="Review", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Review request sent! Data room opened: {channel.mention}", ephemeral=True)

        # Offload the slow Groq API request asynchronously
        async def fetch_ai_assessment():
            try:
                loop = asyncio.get_event_loop()
                def call_groq():
                    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                    ai_prompt = (
                        f"You are a professional server unban appeal screener. Review this argument:\n"
                        f"Account: {self.username.value}\nDefense Argument: {self.reason.value}\n"
                        f"Give a short 2-sentence summary telling staff if the user sounds honest and detailed, or if they are giving standard fake unban excuses like 'it was my brother'."
                    )
                    completion = client.chat.completions.create(
                        model="llama3-8b-8192",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.5,
                        max_tokens=150
                    )
                    return completion.choices[0].message.content
                
                ai_assessment = await loop.run_in_executor(None, call_groq)
            except Exception as e:
                ai_assessment = f"⚠️ *AI triage processing error: {e}*"

            embed.set_field_at(3, name="🤖 Core AI Pre-Screen Evaluation", value=f"*{ai_assessment}*", inline=False)
            await panel_msg.edit(embed=embed)

        asyncio.create_task(fetch_ai_assessment())

# =================================================================
# COMPONENT ROUTING TRIGGERS
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

# =================================================================
# THE MAIN COG CLASS
# =================================================================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        if not self.update_web_metrics.is_running():
            self.update_web_metrics.start()

    async def cog_unload(self):
        self.update_web_metrics.cancel()

    @tasks.loop(seconds=10)
    async def update_web_metrics(self):
        if not self.bot.is_ready():
            return
        try:
            total_servers = len(self.bot.guilds)
            total_members = sum(g.member_count for g in self.bot.guilds if g.member_count)
            
            keep_alive.LIVE_STATS["servers"] = total_servers
            keep_alive.LIVE_STATS["users"] = total_members
            keep_alive.LIVE_STATS["processed"] = processed_cases_counter
        except Exception as e:
            print(f"Metrics Sync Error: {e}")

    @app_commands.command(name="adduiplayerreport", description="Deploy the custom incident reporting layout center")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME: 
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🛡️ Integrity Operations Center", description="See someone breaking guidelines or using exploits? Click below to brief our staff agents.", color=discord.Color.dark_red())
        await channel.send(embed=embed, view=ReportButtonView())
        await interaction.followup.send("✅ Security interface deployed!", ephemeral=True)

    @app_commands.command(name="adduiappealban", description="Deploy the custom account restriction appeal desk")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_appeal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME: 
            return await interaction.response.send_message("❌ Restricted command.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="⚖️ Enforcement Appeal Operations", description="If an action was taken against your account in error, present your arguments below.", color=discord.Color.from_rgb(32, 34, 37))
        await channel.send(embed=embed, view=AppealButtonView())
        await interaction.followup.send("✅ Appeal interface deployed!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
