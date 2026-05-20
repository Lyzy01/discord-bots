import discord
from discord import app_commands
from discord.ext import commands
import io
from datetime import datetime

# Initialize application intents configuration
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="!", intents=intents)

# Simulated in-memory database cluster for tracking AI query contexts per user
AI_CONTEXT_VAULT = {}


# =========================================================================
# 🛡️ SECURITY & CONTEXT HOOKS
# =========================================================================

def is_authorized_staff(interaction: discord.Interaction) -> bool:
    """
    Validates administrative permissions.
    Bypasses for server owners or users with the Administrator permission flag.
    Otherwise, scans member roles for key management title keywords.
    """
    if interaction.user.id == interaction.guild.owner_id or interaction.user.guild_permissions.administrator:
        return True
    
    staff_keywords = ["admin", "moderator", "staff", "owner"]
    return any(role.name.lower() in staff_keywords for role in interaction.user.roles)

def is_ticket_channel(channel_name: str) -> bool:
    """Restricts command executions to custom administrative channels."""
    return "incident-" in channel_name or "appeal-" in channel_name


# =========================================================================
# 🤖 USER INTERACTIONS (AI CONTEXT STACK)
# =========================================================================

@bot.tree.command(name="ai", description="🧠 Transmit queries into Ly's dialogue engine stack tracking context.")
@app_commands.describe(prompt="Your message or query for the AI engine.")
async def ai_command(interaction: discord.Interaction, prompt: str):
    await interaction.response.defer(ephemeral=False)
    user_id = interaction.user.id
    
    if user_id not in AI_CONTEXT_VAULT:
        AI_CONTEXT_VAULT[user_id] = []
        
    AI_CONTEXT_VAULT[user_id].append(f"User: {prompt}")
    
    history_depth = len(AI_CONTEXT_VAULT[user_id])
    ai_response = f"🧠 **Ly's AI Core Engine**\nProcessed your prompt. (Current context depth: {history_depth} interactions).\n\n*Short-term dialogue memory bank contains this thread sequence sample.*"
    
    AI_CONTEXT_VAULT[user_id].append(f"AI: {ai_response}")
    await interaction.followup.send(ai_response)


@bot.tree.command(name="ai_forget", description="🧹 Cleanse your personal short-term dialogue storage bank context.")
async def ai_forget_command(interaction: discord.Interaction):
    user_id = interaction.user.id
    if user_id in AI_CONTEXT_VAULT:
        del AI_CONTEXT_VAULT[user_id]
        msg = "🧹 **Context Rebooted:** Your short-term dialogue memory bank has been cleanly purged."
    else:
        msg = "ℹ️ No active structural context data was found stored under your identity profile."
        
    await interaction.response.send_message(msg, ephemeral=True)


# =========================================================================
# 🎟️ TICKET MANAGEMENT ACTIONS (CORRIDOR OVERRIDES)
# =========================================================================

@bot.tree.command(name="add", description="👤 Grant visibility access overrides to a witness or secondary user.")
@app_commands.describe(user="The server member to invite into this ticket.")
async def add_command(interaction: discord.Interaction, user: discord.Member):
    if not is_ticket_channel(interaction.channel.name):
        await interaction.response.send_message("❌ This command can only be executed inside an active ticket corridor.", ephemeral=True)
        return

    await interaction.channel.set_permissions(user, read_messages=True, send_messages=True, view_channel=True)
    
    embed = discord.Embed(
        title="👤 Access Overrides Expanded",
        description=f"{interaction.user.mention} has added {user.mention} to this private room.",
        color=discord.Color.blue()
    )
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="remove", description="🚪 Strip visibility overrides and evict a witness from this channel.")
@app_commands.describe(user="The server member to remove.")
async def remove_command(interaction: discord.Interaction, user: discord.Member):
    if not is_ticket_channel(interaction.channel.name):
        await interaction.response.send_message("❌ This command can only be executed inside an active ticket corridor.", ephemeral=True)
        return

    await interaction.channel.set_permissions(user, overwrite=None)
    
    embed = discord.Embed(
        title="🚪 Access Overrides Revoked",
        description=f"{interaction.user.mention} cleanly removed {user.mention} from this corridor's overrides.",
        color=discord.Color.orange()
    )
    await interaction.response.send_message(embed=embed)


# =========================================================================
# 🛡️ STAFF DISPATCH PROCEDURES
# =========================================================================

@bot.tree.command(name="claim", description="🔒 Staff Only: Assign this specific ticket corridor to your handling queue.")
async def claim_command(interaction: discord.Interaction):
    if not is_authorized_staff(interaction):
        await interaction.response.send_message("❌ **Access Denied:** Your identity profile lacks required administrative permissions.", ephemeral=True)
        return

    if not is_ticket_channel(interaction.channel.name):
        await interaction.response.send_message("❌ This command can only be executed inside an active ticket room (`#incident-` or `#appeal-`).", ephemeral=True)
        return

    # Update metadata state of the text channel string
    await interaction.channel.edit(topic=f"Case currently handled by: {interaction.user.name} (ID: {interaction.user.id})")

    embed = discord.Embed(
        title="🔒 Case Corridor Claimed",
        description=f"This ticket environment has been officially assigned to and locked by {interaction.user.mention}.\n\n*Other moderators, please check with the claimant before intervening.*",
        color=discord.Color.from_rgb(16, 185, 129)
    )
    embed.set_footer(text=f"Claimed at {datetime.utcnow().strftime('%H:%M:%S')} UTC")
    await interaction.response.send_message(embed=embed)


@bot.tree.command(name="transcript", description="📑 Staff Only: Compile complete room message histories into an archive text log.")
async def transcript_command(interaction: discord.Interaction):
    if not is_authorized_staff(interaction):
        await interaction.response.send_message("❌ **Access Denied:** Your identity profile lacks required administrative permissions.", ephemeral=True)
        return

    await interaction.response.defer(ephemeral=False)

    log_header = (
        f"========================================================\n"
        f"          LY'S AUTOMATION VAULT ARCHIVE TRANSCRIPT      \n"
        f"========================================================\n"
        f"Channel Corridor : #{interaction.channel.name}\n"
        f"Export Initiated : {interaction.user} ({interaction.user.id})\n"
        f"Timestamp (UTC)  : {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"========================================================\n\n"
    )
    
    log_lines = []

    # Stream history iterations sequentially up to a 2000 message block depth
    async for message in interaction.channel.history(limit=2000, oldest_first=True):
        timestamp = message.created_at.strftime('%Y-%m-%d %H:%M:%S')
        content = message.content if message.content else "[Embedded/System layout content blocks]"
        
        attachments = ""
        if message.attachments:
            attachments = f" [Media Attachments: {', '.join([a.url for a in message.attachments])}]"

        log_lines.append(f"[{timestamp}] {message.author} ({message.author.id}): {content}{attachments}")

    full_transcript = log_header + "\n".join(log_lines)
    
    # Pack memory buffer streams directly to avoid hardware write locks
    file_buffer = io.BytesIO(full_transcript.encode('utf-8'))
    discord_file = discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt")

    # Securely route logs straight to automated room if it exists
    audit_vault_channel = discord.utils.get(interaction.guild.text_channels, name="staff-audit-logs")
    
    if audit_vault_channel:
        await audit_vault_channel.send(
            content=f"📑 **New Transcript Archived Record**\nCorridor: `{interaction.channel.name}`\nAuthorized Staff: {interaction.user.mention}",
            file=discord_file
        )
        
        file_buffer.seek(0)
        local_room_copy = discord.File(fp=file_buffer, filename=f"transcript-{interaction.channel.name}.txt")
        await interaction.followup.send(
            content="✅ System has safely compiled the room records and transmitted them straight into your `#staff-audit-logs` channel.", 
            file=local_room_copy
        )
    else:
        await interaction.followup.send(
            content="⚠️ Transcript generated successfully! (Note: Create a `#staff-audit-logs` room to route this backup automated string automatically):", 
            file=discord_file
        )


# =========================================================================
# ENGINE STARTUP SYNC SEQUENCE
# =========================================================================

@bot.event
async def on_ready():
    print(f"Logged in successfully as: {bot.user} (ID: {bot.user.id})")
    try:
        # Synchronizes application command tree vectors globally with Discord API
        synced_commands = await bot.tree.sync()
        print(f"Global Command Trees mapped. Synced {len(synced_commands)} application endpoints safely.")
    except Exception as error:
        print(f"Encountered an internal setup sync conflict error: {error}")

# Run utilizing your secret application token parameters
bot.run("YOUR_BOT_TOKEN_HERE")
