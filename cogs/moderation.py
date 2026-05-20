import discord
from discord import app_commands
from discord.ext import commands
from datetime import timedelta
import json, os

WARN_FILE = "warnings.json"

def load_warns():
    return json.load(open(WARN_FILE)) if os.path.exists(WARN_FILE) else {}

def save_warns(data):
    with open(WARN_FILE, 'w') as f:
        json.dump(data, f, indent=2)

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ban", description="Ban a member from the server")
    @app_commands.describe(member="Member to ban", reason="Reason for the ban")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Cannot ban someone with equal or higher role!", ephemeral=True)
        try:
            await member.send(f"🔨 You were **banned** from **{interaction.guild.name}**\nReason: {reason}")
        except: pass
        await member.ban(reason=reason)
        embed = discord.Embed(title="🔨 Member Banned", description=f"**{member}** has been banned.", color=discord.Color.red())
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="By", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="kick", description="Kick a member from the server")
    @app_commands.describe(member="Member to kick", reason="Reason for the kick")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Cannot kick someone with equal or higher role!", ephemeral=True)
        try:
            await member.send(f"👢 You were **kicked** from **{interaction.guild.name}**\nReason: {reason}")
        except: pass
        await member.kick(reason=reason)
        embed = discord.Embed(title="👢 Member Kicked", description=f"**{member}** has been kicked.", color=discord.Color.orange())
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="By", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="mute", description="Timeout (mute) a member")
    @app_commands.describe(member="Member to mute", duration="Duration in minutes", reason="Reason")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member, duration: int = 10, reason: str = "No reason provided"):
        if member.top_role >= interaction.user.top_role:
            return await interaction.response.send_message("❌ Cannot mute someone with equal or higher role!", ephemeral=True)
        await member.timeout(timedelta(minutes=duration), reason=reason)
        embed = discord.Embed(title="🔇 Member Muted", description=f"**{member}** muted for **{duration} minutes**.", color=discord.Color.orange())
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="By", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="unmute", description="Remove timeout from a member")
    @app_commands.describe(member="Member to unmute")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        await member.timeout(None)
        embed = discord.Embed(title="🔊 Member Unmuted", description=f"**{member}** has been unmuted.", color=discord.Color.green())
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="clear", description="Delete messages in the channel")
    @app_commands.describe(amount="Number of messages to delete (1-100)")
    @app_commands.checks.has_permissions(manage_messages=True)
    async def clear(self, interaction: discord.Interaction, amount: int = 5):
        if not 1 <= amount <= 100:
            return await interaction.response.send_message("❌ Amount must be 1–100!", ephemeral=True)
        await interaction.response.defer(ephemeral=True)
        deleted = await interaction.channel.purge(limit=amount)
        await interaction.followup.send(f"🗑️ Deleted **{len(deleted)}** messages.", ephemeral=True)

    @app_commands.command(name="warn", description="Warn a member")
    @app_commands.describe(member="Member to warn", reason="Reason for warning")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def warn(self, interaction: discord.Interaction, member: discord.Member, reason: str = "No reason provided"):
        warns = load_warns()
        gid, uid = str(interaction.guild.id), str(member.id)
        warns.setdefault(gid, {}).setdefault(uid, [])
        warns[gid][uid].append({"reason": reason, "by": str(interaction.user), "time": discord.utils.utcnow().isoformat()})
        save_warns(warns)
        count = len(warns[gid][uid])
        try:
            await member.send(f"⚠️ **Warning** in **{interaction.guild.name}**\nReason: {reason}\nTotal warnings: {count}")
        except: pass
        embed = discord.Embed(title="⚠️ Member Warned", description=f"**{member}** — Warning #{count}", color=discord.Color.yellow())
        embed.add_field(name="Reason", value=reason)
        embed.add_field(name="By", value=interaction.user.mention)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="warnings", description="View warnings for a member")
    @app_commands.describe(member="Member to check")
    async def warnings_cmd(self, interaction: discord.Interaction, member: discord.Member):
        warns = load_warns()
        user_warns = warns.get(str(interaction.guild.id), {}).get(str(member.id), [])
        embed = discord.Embed(title=f"⚠️ Warnings — {member}", color=discord.Color.yellow())
        if not user_warns:
            embed.description = "✅ No warnings found!"
        else:
            for i, w in enumerate(user_warns, 1):
                embed.add_field(name=f"#{i}", value=f"**Reason:** {w['reason']}\n**By:** {w['by']}", inline=False)
        await interaction.response.send_message(embed=embed)

    @ban.error
    @kick.error
    @mute.error
    @clear.error
    @warn.error
    async def perm_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.MissingPermissions):
            await interaction.response.send_message("❌ You don't have permission for this command!", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Moderation(bot))
