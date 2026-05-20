import discord
from discord import app_commands
from discord.ext import commands

# Replace this string with your exact Discord personal account Username
OWNER_USERNAME = "kimmendez01"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------------------------------
    # DM Gatekeeper Event Listener
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # Ignore messages sent by the bot itself to prevent infinite loops
        if message.author.id == self.bot.user.id:
            return

        # Check if the message is happening inside a DM channel
        if isinstance(message.channel, discord.DMChannel):
            # If the sender is you (kimmendez01), let it pass completely!
            if message.author.name == OWNER_USERNAME:
                return
            
            # If anyone else tries to DM the bot, block them and send the warning
            try:
                await message.channel.send("❌ Oops, you need higher permission to dm me!")
            except discord.Forbidden:
                # In case their DMs are completely locked down
                pass

    # -------------------------------------------------------------
    # Administrative Command: /viewservers
    # -------------------------------------------------------------
    @app_commands.command(name="viewservers", description="[Admin Only] View all servers this bot is active in")
    async def view_servers(self, interaction: discord.Interaction):
        # Security Check: Reject if anyone other than kimmendez01 runs it
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ This administrative tool is restricted.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        guild_list = []
        # Loop through all servers the bot is connected to
        for guild in self.bot.guilds:
            guild_list.append(f"• **{guild.name}** *(Members: {guild.member_count} | ID: {guild.id})*")
        
        # Format the list output beautifully
        server_output = "\n".join(guild_list) if guild_list else "Not currently deployed in any servers."
        
        embed = discord.Embed(
            title="🌐 Active Server Deployments",
            description=server_output,
            color=discord.Color.blue()
        )
        embed.set_footer(text=f"Total Connections: {len(self.bot.guilds)}")
        await interaction.followup.send(embed=embed)

    # -------------------------------------------------------------
    # Administrative Command: /gbannounce
    # -------------------------------------------------------------
    @app_commands.command(name="gbannounce", description="[Admin Only] Broadcast a global announcement to all servers")
    @app_commands.describe(message="The announcement text to blast globally")
    async def global_announce(self, interaction: discord.Interaction, message: str):
        # Security Check: Reject if anyone other than kimmendez01 runs it
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ This administrative tool is restricted.", ephemeral=True)
        
        # Defer immediately since broadcasting to many servers can take several seconds
        await interaction.response.defer(ephemeral=True)
        
        success_count = 0
        failed_count = 0

        # Build a beautiful, official announcement embed
        embed = discord.Embed(
            title="📢 Global Broadcast Notification",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Sent by Bot Administration • {interaction.user.display_name}")

        # Send this message to the system/default text channel of EVERY server
        for guild in self.bot.guilds:
            # Look for the best channel to send to (system channel, rules channel, or first text channel)
            target_channel = guild.system_channel or guild.rules_channel
            
            if not target_channel:
                # If no system channel is set, pick the first available text channel it can write in
                for channel in guild.text_channels:
                    if channel.permissions_for(guild.me).send_messages:
                        target_channel = channel
                        break

            if target_channel:
                try:
                    await target_channel.send(embed=embed)
                    success_count += 1
                except Exception:
                    failed_count += 1
            else:
                failed_count += 1

        await interaction.followup.send(
            f"✅ **Broadcast Complete!**\n🚀 Successfully sent to `{success_count}` servers.\n⚠️ Failed to deliver in `{failed_count}` servers due to permissions."
        )

async def setup(bot):
    await bot.add_cog(Admin(bot))
