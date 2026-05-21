import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from groq import Groq
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
            msg = "🛡️ **Ly's Security Operations Notice:** Your recently filed incident report has been thoroughly investigated and **APPROVED** by our team. Action has been taken against the target offender."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Excellent news! Your enforcement appeal has been formally **APPROVED** upon review. Your account status is being restored."

        if self.target_user_id:
            try: 
                user = await interaction.client.fetch_user(self.target_user_id)
                await user.send(msg)
            except Exception: 
                pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Approval", self.target_user_id, self.raw_fields, "APPROVED", interaction.user)
        
        await asyncio.sleep(1)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Failed to delete channel: {e}")

    @discord.ui.button(label="❌ Deny Case", style=discord.ButtonStyle.danger, custom_id="panel_deny_case")
    async def deny_case(self, interaction: discord.Interaction, button: discord.ui.Button):
        global processed_cases_counter
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied: Requires a higher-rank Staff role.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        processed_cases_counter += 1
        
        if self.ticket_type == "Incident":
            msg = "🛡️ **Ly's Security Operations Notice:** Your incident report submission has been reviewed and **DENIED**. Context or verification data was insufficient."
        else:
            msg = "⚖️ **Ly's Review Desk Notice:** Your enforcement appeal has been reviewed and **DENIED**. The restriction penalty remains absolute."

        if self.target_user_id:
            try: 
                user = await interaction.client.fetch_user(self.target_user_id)
                await user.send(msg)
            except Exception: 
                pass

        await send_audit_archive(interaction.guild, f"{self.ticket_type} Rejection", self.target_user_id, self.raw_fields, "DENIED", interaction.user)

        await asyncio.sleep(1)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Failed to delete channel: {e}")

    @discord.ui.button(label="🔒 Cancel Session", style=discord.ButtonStyle.secondary, custom_id="panel_cancel_session")
    async def cancel_session(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ Access Denied: Requires a higher-rank Staff role.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        self.parse_embed_data(interaction)
        
        await send_audit_archive(interaction.guild, f"{self.ticket_type} Wiped", self.target_user_id, self.raw_fields, "TERMINATED/CANCELLED", interaction.user)
        
        await asyncio.sleep(1)
        try:
            await interaction.channel.delete()
        except Exception as e:
            print(f"Failed to delete channel: {e}")

# =================================================================
# BUG TICKETING ENGINE INTERACTION SYSTEM
# =================================================================
class BugReportModal(discord.ui.Modal, title="Report Bugs & Errors"):
    bug_title = discord.ui.TextInput(label="Command or Feature Affected", placeholder="e.g., /ai or leveling progression", required=True)
    details = discord.ui.TextInput(label="Error Details / Reproduction Steps", style=discord.TextStyle.paragraph, placeholder="Explain carefully what happened and what error it showed...", required=True)

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild
        user = interaction.user

        target_channel = discord.utils.get(guild.text_channels, name="report-here")
        if not target_channel:
            target_channel = interaction.channel

        embed = discord.Embed(
            title="🛡️ Integrity Operations Center",
            description="A new system bug or bot execution error has been registered below.",
            color=discord.Color.red()
        )
        embed.add_field(name="🐛 System Target", value=f"`{self.bug_title.value}`", inline=False)
        embed.add_field(name="📝 Defect Log Payload", value=self.details.value, inline=False)
        embed.set_footer(text=f"Report Submitter: {user.name} | ID: {user.id}")

        view = BugReportDisplayView()

        await target_channel.send(embed=embed, view=view)
        await interaction.followup.send("✅ **System Log Transmitted!** Your bug report has been forwarded directly to the bot developer panel.", ephemeral=True)

class BugReportDisplayView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    
    @discord.ui.button(label="File Incident Report 🚩", style=discord.ButtonStyle.danger, custom_id="bug_ui_disabled_btn", disabled=True)
    async def visual_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        pass

# =================================================================
# PUBLIC POP-UP MODALS 
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
        embed.set_footer(text=f"Dispatched by: {interaction.user.name} | ID: {interaction.user.id}")
        
        saved_fields = {"Target Player": self.username.value, "Report Details": self.reason.value, "Media Links": self.evidence.value}
        
        await channel.send(embed=embed, view=StaffControlPanel(target_user_id=interaction.user.id, ticket_type="Incident", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Case registered! Secure channel opened: {channel.mention}", ephemeral=True)

        async def fetch_ai_assessment():
            try:
                loop = asyncio.get_event_loop()
                def call_groq():
                    client = Groq(api_key=os.getenv("GROQ_API_KEY"))
                    ai_prompt = (
                        f"You are a professional game server moderation scanner. Review this report:\n"
                        f"Target: {self.username.value}\nReason: {self.reason.value}\nEvidence Link: {self.evidence.value}\n"
                        f"Give a short 2-sentence feedback label summary telling staff if it seems real, missing clear facts, or potentially spam."
                    )
                    completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.4,
                        max_tokens=150
                    )
                    return completion.choices[0].message.content
                
                ai_assessment = await loop.run_in_executor(None, call_groq)
            except Exception as e:
                ai_assessment = f"⚠️ *AI triage processing error: {e}*"

            log_channel = discord.utils.get(guild.text_channels, name="staff-audit-logs")
            if log_channel:
                description_text = (
                    f"**Target Case Room:** {channel.mention}\n\n"
                    f"**AI Analysis:**\n*{ai_assessment}*\n\n"
                    f"⚠️ *Note: This Core AI Pre-Screen Triage is not always accurate, so please review the case carefully.*"
                )
                ai_embed = discord.Embed(title="🤖 Core AI Pre-Screen Triage", description=description_text, color=discord.Color.blurple())
                ai_embed.set_footer(text=f"Submitted by {interaction.user.name} | Confidential Staff View Only")
                await log_channel.send(embed=ai_embed)

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
        embed.set_footer(text=f"Awaiting review panel decision... | ID: {interaction.user.id}")
        
        saved_fields = {"Account Username": self.username.value, "Defense Reasons Given": self.reason.value}
        
        await channel.send(embed=embed, view=StaffControlPanel(target_user_id=interaction.user.id, ticket_type="Review", raw_fields=saved_fields))
        await interaction.followup.send(f"✅ Review request sent! Data room opened: {channel.mention}", ephemeral=True)

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
                        model="llama-3.1-8b-instant",
                        messages=[{"role": "user", "content": ai_prompt}],
                        temperature=0.4,
                        max_tokens=150
                    )
                    return completion.choices[0].message.content
                
                ai_assessment = await loop.run_in_executor(None, call_groq)
            except Exception as e:
                ai_assessment = f"⚠️ *AI triage processing error: {e}*"

            log_channel = discord.utils.get(guild.text_channels, name="staff-audit-logs")
            if log_channel:
                description_text = (
                    f"**Target Appeal Room:** {channel.mention}\n\n"
                    f"**AI Analysis:**\n*{ai_assessment}*\n\n"
                    f"⚠️ *Note: This Core AI Pre-Screen Triage is not always accurate, so please review the case carefully.*"
                )
                ai_embed = discord.Embed(title="🤖 Core AI Pre-Screen Triage", description=description_text, color=discord.Color.blurple())
                ai_embed.set_footer(text=f"Submitted by {interaction.user.name} | Confidential Staff View Only")
                await log_channel.send(embed=ai_embed)

        asyncio.create_task(fetch_ai_assessment())

# =================================================================
# COMPONENT ROUTING TRIGGERS (WITH CUSTOM IDS FOR PERSISTENCE)
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

class GeneralBugDeployView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)
    @discord.ui.button(label="Report Bot Bugs & Errors 🐛", style=discord.ButtonStyle.secondary, custom_id="trigger_bug_report_modal")
    async def click_bug(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_modal(BugReportModal())

# =================================================================
# THE MAIN COG CLASS WITH TICKET MANAGEMENT COMMANDS
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

    # --- SET ROLE COLOR COMMAND (FIXED & FULLY FUNCTIONAL) ---
    @app_commands.command(name="setrolecolor", description="🎨 Higher Rank Only: Alter the display hexadecimal color hex code profile of a target role.")
    @app_commands.describe(role="The server role profile to alter", hex_code="The new Color Hex value (e.g. #FF5555 or 00FF00)")
    async def set_role_color(self, interaction: discord.Interaction, role: discord.Role, hex_code: str):
        # Restriction Check: Only Staff/Higher Ranks can run this moderation command
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        # Clean up the hex code string payload input formatting
        clean_hex = hex_code.replace("#", "").strip()
        
        try:
            # Convert hex string data structure directly into a discord integer tuple color
            rgb_color = tuple(int(clean_hex[i:i+2], 16) for i in (0, 2, 4))
            new_color = discord.Color.from_rgb(*rgb_color)
        except Exception:
            return await interaction.followup.send("❌ **Format Error:** Invalid Hex Code entry found. Please supply data mirroring format patterns like `#FF5555` or `00AAFF`.", ephemeral=True)

        try:
            await role.edit(color=new_color, reason=f"Color update requested by {interaction.user.name}")
            
            embed = discord.Embed(
                title="🎨 System Database Updated", 
                description=f"Successfully edited structural properties for configuration role profile: {role.mention}.\n**New Hex Profile:** `{hex_code.upper()}`", 
                color=new_color
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send("❌ **Hierarchy Error:** The bot cannot update that specific role configuration layout because it resides higher up in structural hierarchy lists than the bot's role profile.", ephemeral=True)
        except Exception as e:
            await interaction.followup.send(f"❌ An error occurred trying to save details: `{e}`", ephemeral=True)

    # --- ADD ACCESS OVERRIDE COMMAND ---
    @app_commands.command(name="add", description="👤 Higher Rank Only: Grant ticket room visibility overrides directly to a member.")
    @app_commands.describe(user="The server member to invite into this ticket room")
    async def add_command(self, interaction: discord.Interaction, user: discord.Member):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name):
            return await interaction.response.send_message("❌ This command can only be used inside an active ticket room.", ephemeral=True)
        
        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
        embed = discord.Embed(title="👤 Access Expanded", description=f"{interaction.user.mention} added {user.mention} to this channel.", color=discord.Color.blue())
        await interaction.response.send_message(embed=embed)

    # --- REMOVE ACCESS OVERRIDE COMMAND ---
    @app_commands.command(name="remove", description="🚪 Higher Rank Only: Strip visibility overrides and evict a member from this ticket.")
    @app_commands.describe(user="The server member to remove")
    async def remove_command(self, interaction: discord.Interaction, user: discord.Member):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name):
            return await interaction.response.send_message("❌ This command can only be used inside an active ticket room.", ephemeral=True)
        
        await interaction.channel.set_permissions(user, overwrite=None)
        embed = discord.Embed(title="🚪 Access Revoked", description=f"{interaction.user.mention} removed {user.mention} from this channel.", color=discord.Color.orange())
        await interaction.response.send_message(embed=embed)

    # --- CLAIM CORRIDOR COMMAND ---
    @app_commands.command(name="claim", description="🔒 Higher Rank Only: Assign this specific ticket corridor to your handling queue.")
    async def claim_command(self, interaction: discord.Interaction):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        if not is_ticket_channel(interaction.channel.name):
            return await interaction.response.send_message("❌ This command can only be used inside an active ticket room.", ephemeral=True)

        await interaction.channel.edit(topic=f"Case currently handled by: {interaction.user.name}")
        embed = discord.Embed(title="🔒 Case Corridor Claimed", description=f"This ticket environment has been officially assigned to {interaction.user.mention}.", color=discord.Color.from_rgb(16, 185, 129))
        await interaction.response.send_message(embed=embed)

    # --- TRANSCRIPT GENERATOR COMMAND ---
    @app_commands.command(name="transcript", description="📑 Higher Rank Only: Compile complete room message histories into an archive text log.")
    async def transcript_command(self, interaction: discord.Interaction):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)

        await interaction.response.defer(ephemeral=False)
        log_header = f"=== ARCHIVE TRANSCRIPT FOR #{interaction.channel.name} ===\nExported: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC\n=========================================\n\n"
        log_lines = []

        async for message in interaction.channel.history(limit=2000, oldest_first=True):
            timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
            content = message.content if message.content else "[Embedded/System Layout Content]"
            attachments = f" [Attachments: {', '.join([a.url for a in message.attachments])}]" if message.attachments else ""
            log_lines.append(f"[{timestamp}] {message.author}: {content}{attachments}")

        full_transcript = log_header + "\n".join(log_lines)
        file_buffer = io.BytesIO(full_transcript.encode('utf-8'))
        discord_file = discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt")

        audit_vault_channel = discord.utils.get(interaction.guild.text_channels, name="staff-audit-logs")
        if audit_vault_channel:
            await audit_vault_channel.send(content=f"📑 **New Transcript Record:** `{interaction.channel.name}` by {interaction.user.mention}", file=discord_file)
            file_buffer.seek(0)
            local_room_copy = discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt")
            await interaction.followup.send(content="✅ Transcript saved to `#staff-audit-logs`.", file=local_room_copy)
        else:
            await interaction.followup.send(content="⚠️ Transcript compiled successfully! (Tip: Create a `#staff-audit-logs` channel to auto-route):", file=discord_file)

    # --- REPLY VIA BOT DM COMMAND ---
    @app_commands.command(name="addreportbugs", description="✉️ Higher Rank Only: Transmit a direct message reply panel response to a bug submitter.")
    @app_commands.describe(user_id="The long numerical Discord ID string of the target user", message="The resolution message to DM")
    async def add_report_bugs(self, interaction: discord.Interaction, user_id: str, message: str):
        if not is_authorized_staff(interaction):
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        try:
            target_id = int(user_id)
        except ValueError:
            return await interaction.followup.send("❌ Error: Target User ID string must contain numbers only.", ephemeral=True)

        try:
            target_user = await self.bot.fetch_user(target_id)
        except Exception:
            return await interaction.followup.send("❌ Error: Could not locate that user profile index on Discord.", ephemeral=True)

        dm_embed = discord.Embed(
            title="✉️ Official Core Developer Response",
            description=f"Hello **{target_user.name}**, you have received an action status update regarding your submitted bug report.",
            color=discord.Color.purple()
        )
        dm_embed.add_field(name="💬 Action & Resolution Notes", value=f"```text\n{message}\n```", inline=False)
        dm_embed.set_footer(text="Sent securely from Ly's Operational Support Center")

        try:
            await target_user.send(embed=dm_embed)
            await interaction.followup.send(f"🚀 **Transmission Dispatched!** Securely messaged {target_user.mention} with your notes.", ephemeral=True)
        except discord.Forbidden:
            await interaction.followup.send(f"❌ Transmission Blocked: Unable to direct message {target_user.name} because their privacy blocks are enabled.", ephemeral=True)

    # --- DEPLOY PLAYER REPORT UI ---
    @app_commands.command(name="adduiplayerreport", description="Deploy the custom incident reporting layout center")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_report(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_authorized_staff(interaction): 
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="🛡️ Integrity Operations Center", description="See someone breaking guidelines or using exploits? Click below to brief our staff agents.", color=discord.Color.dark_red())
        await channel.send(embed=embed, view=ReportButtonView())
        await interaction.followup.send("✅ Security interface deployed!", ephemeral=True)

    # --- DEPLOY ENFORCEMENT APPEAL UI ---
    @app_commands.command(name="adduiappealban", description="Deploy the custom account restriction appeal desk")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_appeal(self, interaction: discord.Interaction, channel: discord.TextChannel):
        if not is_authorized_staff(interaction): 
            return await interaction.response.send_message("❌ **Access Denied:** Requires a higher-rank Staff role.", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(title="⚖️ Enforcement Appeal Operations", description="If an action was taken against your account in error, present your arguments below.", color=discord.Color.from_rgb(32, 34, 37))
        await channel.send(embed=embed, view=AppealButtonView())
        await interaction.followup.send("✅ Appeal interface deployed!", ephemeral=True)

    # --- OWNER-ONLY DEPLOY INTERFACE: BUG SYSTEM CENTER ---
    @app_commands.command(name="adduibugreports", description="👑 OWNER ONLY: Deploy the general bug tracking interactive option module.")
    @app_commands.describe(channel="The target channel for the interface")
    async def add_ui_bugs(self, interaction: discord.Interaction, channel: discord.TextChannel):
        # STRICTOR PERMISSION LOCK: Only you can run this command
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ **Strict Access Denied:** This deployment setup script is locked exclusively to the core bot creator account.", ephemeral=True)
            
        await interaction.response.defer(ephemeral=True)
        
        embed = discord.Embed(
            title="🐛 Core Defect & Bug Tracking",
            description="Encountered an internal glitch, script freeze, or layout problem with the bot? Click the button below to submit a system log to the developer team.",
            color=discord.Color.dark_gray()
        )
        await channel.send(embed=embed, view=GeneralBugDeployView())
        await interaction.followup.send("✅ Bug reporting interaction center deployed successfully!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
