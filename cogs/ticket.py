import discord
from discord import app_commands
from discord.ext import commands

OWNER_USERNAME = "kimmendez01"

class Tickets(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------------------------------
    # COMMAND 1: /appeal (For Ban/Roblox Appeals)
    # -------------------------------------------------------------
    @app_commands.command(name="appeal", description="Submit a ban or Roblox action appeal to the staff team")
    @app_commands.describe(
        username="Your Roblox or Discord Username",
        reason="Why should your ban be reviewed or appealed?"
    )
    async def appeal_command(self, interaction: discord.Interaction, username: str, reason: str):
        await interaction.response.defer(ephemeral=True)
        guild = interaction.guild

        # 1. Define the names of high-level roles allowed to handle appeals
        # The bot will look for ANY role containing these words
        admin_keywords = ["admin", "moderator", "staff", "owner"]

        # 2. Set up base permissions: Bot and User can read the ticket
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False), # Hide from everyone else
            guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True), # Let bot see it
            interaction.user: discord.PermissionOverwrite(read_messages=True, send_messages=True) # Let user see it
        }

        # 3. Automatically scan the server and give access to your high roles
        staff_found = False
        for role in guild.roles:
            if any(keyword in role.name.lower() for keyword in admin_keywords):
                overwrites[role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                staff_found = True

        # 4. Create a clean category or channel for the appeal review
        channel_name = f"appeal-{interaction.user.name}"
        try:
            ticket_channel = await guild.create_text_channel(name=channel_name, overwrites=overwrites)
            
            # 5. Build an official administrative ticket box inside the new channel
            embed = discord.Embed(
                title="⚖️ New Action Appeal Case Opened",
                description="Our high-ranking staff team will review your case details shortly.",
                color=discord.Color.red()
            )
            embed.add_field(name="👤 Target Account", value=username, inline=True)
            embed.add_field(name="🆔 Submitted By", value=interaction.user.mention, inline=True)
            embed.add_field(name="📝 Reason Given", value=reason, inline=False)
            
            staff_notice = "⚠️ *Note: High staff roles have been auto-granted permission to view this channel.*" if staff_found else "⚠️ *Note: No specific 'Admin/Mod' roles were found. Only the server Owner can view this.*"
            embed.set_footer(text=staff_notice)

            await ticket_channel.send(embed=embed)
            await interaction.followup.send(f"✅ Your appeal has been created! Head over to {ticket_channel.mention} to talk to staff.", ephemeral=True)
            
        except Exception as e:
            print(f"Ticket Error: {e}")
            await interaction.followup.send("❌ Failed to generate your ticket channel. Make sure my bot role is at the top of your roles list and has 'Manage Channels' turned on!", ephemeral=True)

    # -------------------------------------------------------------
    # COMMAND 2: /ticket (For Feedback & Bug Reporting)
    # -------------------------------------------------------------
    @app_commands.command(name="ticket", description="Send feedback, report bugs, or request features directly to Ly's AI")
    @app_commands.describe(
        type="Select what kind of ticket you are opening",
        details="Describe your feedback, bug, or idea in detail"
    )
    @app_commands.choices(type=[
        app_commands.Choice(name="Bug Report 🐛", value="Bug Report"),
        app_commands.Choice(name="User Feedback 💬", value="User Feedback"),
        app_commands.Choice(name="Feature Suggestion 💡", value="Feature Suggestion")
    ])
    async def feedback_ticket(self, interaction: discord.Interaction, type: app_commands.Choice[str], details: str):
        await interaction.response.defer(ephemeral=True)

        try:
            # Locate your personal developer user account
            owner = discord.utils.get(self.bot.users, name=OWNER_USERNAME)
            
            if owner:
                # Build a dedicated developer notification dashboard card
                embed = discord.Embed(
                    title=f"📥 New System Ticket: {type.value}",
                    description=details,
                    color=discord.Color.teal()
                )
                embed.set_author(name=f"{interaction.user.display_name} (@{interaction.user.name})", icon_url=interaction.user.avatar.url if interaction.user.avatar else None)
                embed.add_field(name="Source Server", value=interaction.guild.name if interaction.guild else "Direct Message", inline=True)
                embed.add_field(name="User ID", value=f"`{interaction.user.id}`", inline=True)
                embed.set_footer(text="Ly's AI Core Development Hub")

                await owner.send(embed=embed)
                await interaction.followup.send("✨ Thank you! Your feedback/bug report has been submitted directly to my developer database.", ephemeral=True)
            else:
                await interaction.followup.send("❌ Error contacting the core developer. Please try again later.", ephemeral=True)
                
        except Exception as e:
            print(f"Feedback routing failed: {e}")
            await interaction.followup.send("❌ System failure sending your submission ticket.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Tickets(bot))
