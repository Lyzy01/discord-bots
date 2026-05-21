import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
import io
import os
from datetime import datetime
import keep_alive

OWNER_USERNAME = "kimmendez01"

# Counter to log processed files globally across memory resets
processed_cases_counter = 0

def is_authorized_staff(interaction: discord.Interaction) -> bool:
    """Returns True if user is the bot creator or possesses an elevated administrative role."""
    if interaction.user.name == OWNER_USERNAME:
        return True
    admin_keywords = ["admin", "moderator", "staff", "owner"]
    return any(any(k in role.name.lower() for k in admin_keywords) for role in interaction.user.roles)

def is_ticket_channel(channel_name: str) -> bool:
    """Restricts staff commands to target administrative ticket rooms."""
    name_lower = channel_name.lower()
    return "incident-" in name_lower or "appeal-" in name_lower or "review-" in name_lower

# =================================================================
# ADVANCED AUDIT LOG ARCHIVER FUNCTION
# =================================================================
async def send_audit_archive(guild: discord.Guild, title: str, user_id: int, fields: dict, decision: str, staff: discord.User):
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
    audit_embed.add_field(name="👤 Original Submitter", value=f"<@{user_id}> (`{user_id}`)", inline=False)
    
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
# THE THREE-BUTTON STAFF CONTROL PANEL (STABLE PERSISTENCE)
# =================================================================
class StaffControlPanel(discord.ui.View):
    def __init__(self, target_user_id: int = None, ticket_type: str = None, raw_fields: dict = None):
        super().__init__(timeout=None)
        self.target_user_id = target_user_id
        self.ticket_type = ticket_type
        self.raw_fields = raw_fields

    def parse_embed_data(self, interaction: discord.Interaction):
        """Helper to reconstruct structural data if the bot restarted."""
        if self.target_user_id and self.ticket_type and self.raw_fields:
            return True

        try:
            message = interaction.message
            if not message or not message.embeds:
                return False
            
            embed = message.embeds[0]
            
            if "Incident" in embed.title or "Security Core" in embed.title:
                self.ticket_type = "Incident"
            else:
                self.ticket_type = "Review"

            self.raw_fields = {}
            for field in embed.fields:
                if any(k in field.name for k in ["Account", "Player", "Report", "Defense", "Situation", "Verification", "Proof"]):
                    self.raw_fields[field.name] = field.value

            if embed.footer and embed.footer.text and "ID:" in embed.footer.text:
                self.target_user_id = int(embed.footer.text.split("ID:")[-1].strip())
            else:
                for field in embed.fields:
                    if "Discord Contact" in field.name and "<@" in field.value:
                        clean_id = field.value.replace("<@", "").replace(">", "").replace("!", "")
                        self.target_user_id = int(clean_id)
                        break
            
            return self.target_user_id is not None
        except Exception as e:
            print(f"Failed to rebuild panel memory structures: {e}")
            return False

    @discord.ui.button(label="✅ Approve Case", style=discord.ButtonStyle.success, custom_id="panel_approve_case")
    async def approve_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        global processed_cases_counter
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied: Requires a higher-rank Staff role.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        processed_cases_counter += 1
        
        if self.ticket_type == "Incident":
            msg = "🛡️ **Ly's Security Operations Notice:** Your recently filed incident report has been thoroughly investigated and **APPROVED** by our team."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Excellent news! Your enforcement appeal has been formally **APPROVED** upon review."

        if self.target_user_id:
            try: 
                user = await interaction.client.fetch_user(self.target_user_id)
                await user.send(msg)
            except Exception: 
                pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Approval", self.target_user_id, self.raw_fields, "APPROVED", interaction.user)
        try:
            await interaction.channel.delete()
        except Exception:
            pass

    @discord.ui.button(label="❌ Deny Case", style=discord.ButtonStyle.danger, custom_id="panel_deny_case")
    async def deny_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        global processed_cases_counter
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied: Requires a higher-rank Staff role.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        processed_cases_counter += 1
        
        if self.ticket_type == "Incident":
            msg = "🛡️ **Ly's Security Operations Notice:** Your incident report submission has been reviewed and **DENIED**."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Your enforcement appeal has been reviewed and **DENIED**."

        if self.target_user_id:
            try: 
                user = await interaction.client.fetch_user(self.target_user_id)
                await user.send(msg)
            except Exception: 
                pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Rejection", self.target_user_id, self.raw_fields, "DENIED", interaction.user)
        try:
            await interaction.channel.delete()
        except Exception:
            pass

    @discord.ui.button(label="🔒 Cancel Session", style=discord.ButtonStyle.secondary, custom_id="panel_cancel_session")
    async def cancel_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied: Requires a higher-rank Staff role.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        await send_audit_archive(interaction.guild, f"{self.ticket_type} Wiped", self.target_user_id, self.raw_fields, "TERMINATED/CANCELLED", interaction.user)
        try:
            await interaction.channel.delete()
        except Exception:
            pass

# =================================================================
# INTERACTIVE SYSTEMS & MODALS
# =================================================================
class BugReportModal(discord.ui.Modal, title="Report Bugs & Errors"):
    bug_title = discord.ui.TextInput(label="Command or Feature Affected", placeholder="e.g., /ai or leveling progression", required=True)
    details = discord.ui.TextInput(label="Error Details / Reproduction Steps", style=discord.TextStyle.paragraph, placeholder="Explain carefully what happened...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        target_channel = discord.utils.get(interaction.guild.text_channels, name="report-here") or interaction.channel
        
        embed = discord.Embed(title="🛡️ Integrity Operations Center", description="A new system bug has been registered.", color=discord.Color.red())
        embed.add_field(name="🐛 System Target", value=f"`{self.bug_title.value}`", inline=False)
        embed.add_field(name="📝 Defect Log Payload", value=self.details.value, inline=False)
        embed.set_footer(text=f"Report Submitter: {interaction.user.name} | ID: {interaction.user.id}")

        await target_channel.send(embed=embed, view=BugReportDisplayView())
        await interaction.followup.send("✅ **System Log Transmitted!** Forwarded to the developer panel.", ephemeral=True)

class BugReportDisplayView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="File Incident Report 🚩", style=discord.ButtonStyle.danger, custom_id="bug_ui_disabled_btn", disabled=True)
    async def visual_button(self, interaction: discord.Interaction, button: discord.ui.Button): pass

class PlayerReportModal(discord.ui.Modal, title="Submit Incident Report"):
    username = discord.ui.TextInput(label="Target Player Account", placeholder="Username of the rule-breaker", required=True)
    reason = discord.ui.TextInput(label="Incident Context & Details", style=discord.TextStyle.paragraph, required=True)
    evidence = discord.ui.TextInput(label="Proof / Media Evidence Link", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role in guild.roles:
            if any(k in role.name.lower() for k in ["admin", "moderator", "staff", "owner"]):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(name=f"incident-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="🛡️ Security Core: Live Incident Logged", color=discord.Color.dark_orange())
        embed.add_field(name="👤 Flagged Account", value=f"`{self.username.value}`", inline=False)
        embed.add_field(name="📝 Situation Report", value=self.reason.value, inline=False)
        embed.add_field(name="🔗 Attached Verification", value=self.evidence.value, inline=False)
        embed.set_footer(text=f"Dispatched by: {interaction.user.name} | ID: {interaction.user.id}")
        
        saved_fields = {"Target Player": self.username.value, "Report Details": self.reason.value, "Media Links": self.evidence.value}
        await channel.send(embed=embed, view=StaffControlPanel(target_user_id=interaction.user.id, ticket_type="Incident", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Secure channel opened: {channel.mention}", ephemeral=True)

class BanAppealModal(discord.ui.Modal, title="Review Request System"):
    username = discord.ui.TextInput(label="Your In-Game Username", placeholder="The restricted account name", required=True)
    reason = discord.ui.TextInput(label="Case Argument / Defense Statement", style=discord.TextStyle.paragraph, required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True)
        }
        for role in guild.roles:
            if any(k in role.name.lower() for k in ["admin", "moderator", "staff", "owner"]):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

        channel = await guild.create_text_channel(name=f"review-{interaction.user.name}", overwrites=overwrites)
        
        embed = discord.Embed(title="⚖️ Enforcement Review Docket Initiated", color=discord.Color.teal())
        embed.add_field(name="👤 Restricted Account", value=f"`{self.username.value}`", inline=True)
        embed.add_field(name="📝 Defense Arguments", value=self.reason.value, inline=False)
        embed.set_footer(text=f"ID: {interaction.user.id}")
        
        saved_fields = {"Account Username": self.username.value, "Defense Reasons": self.reason.value}
        await channel.send(embed=embed, view=StaffControlPanel(target_user_id=interaction.user.id, ticket_type="Review", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Data room opened: {channel.mention}", ephemeral=True)

# Persistent trigger layouts
class ReportButtonView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="File Incident Report 🚩", style=discord.ButtonStyle.danger, custom_id="trigger_player_report")
    async def click_report(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(PlayerReportModal())

class AppealButtonView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Request Case Review 📑", style=discord.ButtonStyle.primary, custom_id="trigger_ban_appeal")
    async def click_appeal(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BanAppealModal())

class GeneralBugDeployView(discord.ui.View):
    def __init__(self): super().__init__(timeout=None)
    @discord.ui.button(label="Report Bot Bugs & Errors 🐛", style=discord.ButtonStyle.secondary, custom_id="trigger_bug_report_modal")
    async def click_bug(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BugReportModal())

# =================================================================
# COG CLASS INTERFACES
# =================================================================
class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def cog_load(self):
        if not self.update_web_metrics.is_running():
            self.update_web_metrics.start()

    async def cog_unload(self):
        self.update_web_metrics.cancel()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(ReportButtonView())
        self.bot.add_view(AppealButtonView())
        self.bot.add_view(StaffControlPanel())
        self.bot.add_view(GeneralBugDeployView())
        self.bot.add_view(BugReportDisplayView())
        print("🎛 Persistent View listeners safely linked across restarts.")

    @tasks.loop(seconds=10)
    async def update_web_metrics(self):
        if not self.bot.is_ready(): return
        try:
            keep_alive.LIVE_STATS["servers"] = len(self.bot.guilds)
            keep_alive.LIVE_STATS["users"] = sum(g.member_count for g in self.bot.guilds if g.member_count)
            keep_alive.LIVE_STATS["processed"] = processed_cases_counter
        except Exception: pass

    # --- SET ROLE COLOR COMMAND ---
    @app_commands.command(name="setrolecolor", description="🎨 Higher Rank Only: Alter a role's hex color code.")
    @app_commands.describe(role="The server role profile to alter", hex_code="The new Color Hex value (e.g. #FF5555)")
    async def set_role_color(self, interaction: discord.Interaction, role: discord.Role, hex_code: str):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        
        clean_hex = hex_code.replace("#", "").strip()
        try:
            rgb_color = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))
            new_color = discord.Color.from_rgb(*rgb_color)
        except Exception:
            return await interaction.followup.send("❌ **Format Error:** Invalid Hex Code. Use format like `#FF5555`.", ephemeral=True)

        try:
            await role.edit(color=new_color, reason=f"Color update by {interaction.user.name}")
            embed = discord.Embed(title="🎨 Updated", description=f"Altered color profile for: {role.mention}.\n**New Hex:** `{hex_code.upper()}`", color=new_color)
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ **Hierarchy Error:** This role is positioned higher than the bot's own role.", ephemeral=True)

    # --- TICKET CONTROL COMMANDS ---
    @app_commands.command(name="add", description="👤 Higher Rank Only: Grant ticket room visibility overrides.")
    async def add_command(self, interaction: discord.Interaction, user: discord.Member):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name): return await interaction.response.send_message("❌ Not a ticket channel.", ephemeral=True)
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
        await interaction.response.send_message(embed=discord.Embed(title="👤 Access Expanded", description=f"Added {user.mention}.", color=discord.Color.blue()))

    @app_commands.command(name="remove", description="🚪 Higher Rank Only: Strip visibility overrides.")
    async def remove_command(self, interaction: discord.Interaction, user: discord.Member):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name): return await interaction.response.send_message("❌ Not a ticket channel.", ephemeral=True)
        await interaction.channel.set_permissions(user, overwrite=None)
        await interaction.response.send_message(embed=discord.Embed(title="🚪 Access Revoked", description=f"Removed {user.mention}.", color=discord.Color.orange()))

    @app_commands.command(name="claim", description="🔒 Higher Rank Only: Assign this specific ticket.")
    async def claim_command(self, interaction: discord.Interaction):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name): return await interaction.response.send_message("❌ Not a ticket channel.", ephemeral=True)
        await interaction.channel.edit(topic=f"Case handled by: {interaction.user.name}")
        await interaction.response.send_message(embed=discord.Embed(title="🔒 Claimed", description=f"Assigned to {interaction.user.mention}.", color=discord.Color.green()))

    @app_commands.command(name="transcript", description="📑 Higher Rank Only: Compile room message histories.")
    async def transcript_command(self, interaction: discord.Interaction):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        await interaction.response.defer(ephemeral=False)
        
        log_header = f"=== ARCHIVE FOR #{interaction.channel.name} ===\n\n"
        log_lines = []
        async for message in interaction.channel.history(limit=2000, oldest_first=True):
            content = message.content or "[Embed/System Content]"
            log_lines.append(f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] {message.author}: {content}")

        file_buffer = io.BytesIO((log_header + "\n".join(log_lines)).encode('utf-8'))
        discord_file = discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt")
        
        audit = discord.utils.get(interaction.guild.text_channels, name="staff-audit-logs")
        if audit:
            await audit.send(content=f"📑 **Transcript Saved:** `{interaction.channel.name}` by {interaction.user.mention}", file=discord_file)
            file_buffer.seek(0)
            await interaction.followup.send(content="✅ Saved to `#staff-audit-logs`.", file=discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt"))
        else:
            await interaction.followup.send(content="⚠️ Compiled:", file=discord_file)

    @app_commands.command(name="addreportbugs", description="✉️ Higher Rank Only: Send a DM to a bug submitter.")
    async def add_report_bugs(self, interaction: discord.Interaction, user_id: str, message: str):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        try:
            target_user = await self.bot.fetch_user(int(user_id))
            embed = discord.Embed(title="✉️ Developer Response", description=f"Update regarding your bug report:\n```text\n{message}\n```", color=discord.Color.purple())
            await target_user.send(embed=embed)
            await interaction.followup.send(f"🚀 Sent to {target_user.mention}.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ Failed: `{e}`", ephemeral=True)

    @app_commands.command(name="adduiplayerreport", description="Deploy incident reporting layout center")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        await channel.send(embed=discord.Embed(title="🛡️ Integrity Center", description="Click below to report a rule-breaker.", color=discord.Color.red()), view=ReportButtonView())
        await interaction.response.send_message("✅ Deployed!", ephemeral=True)

    @app_commands.command(name="adduiappealban", description="Deploy custom account appeal desk")
    async def add_ui_appeal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_authorized_staff(interaction): return await interaction.response.send_message("❌ **Access Denied**", ephemeral=True)
        await channel.send(embed=discord.Embed(title="⚖️ Appeal Desk", description="Click below to request an account review.", color=discord.Color.blue()), view=AppealButtonView())
        await interaction.response.send_message("✅ Deployed!", ephemeral=True)

    # --- OWNER-ONLY BUG UI DEPLOY ---
    @app_commands.command(name="adduibugreports", description="👑 OWNER ONLY: Deploy bug tracking system layout.")
    async def add_ui_bugs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ **Strict Access Denied: Locked to Bot Owner Only.**", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        await channel.send(embed=discord.Embed(title="🐛 Bug Tracking Center", description="Click below to report bot glitches directly to the developer.", color=discord.Color.dark_grey()), view=GeneralBugDeployView())
        await interaction.followup.send("✅ Bug interface deployed!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
