import discord
from discord import app_commands
from discord.ext import commands

# Keep this as your exact username
OWNER_USERNAME = "kimmendez01"

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # -------------------------------------------------------------
    # Upgraded DM Gatekeeper + ModMail Router
    # -------------------------------------------------------------
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.id == self.bot.user.id:
            return

        if isinstance(message.channel, discord.DMChannel):
            # If it's you messaging the bot, ignore the restriction filter
            if message.author.name == OWNER_USERNAME:
                return
            
            # 1. Alert the regular user that DMs are locked down
            try:
                await message.channel.send("❌ Oops, you need higher permission to dm me! Your message has been forwarded to my developer.")
            except discord.Forbidden:
                pass

            # 2. Forward their ticket message straight to kimmendez01
            try:
                # Search Discord's internal cache to find your user object global account
                owner = discord.utils.get(self.bot.users, name=OWNER_USERNAME)
                
                if owner:
                    # Construct a crisp dashboard ticket box layout
                    embed = discord.Embed(
                        title="📩 New Incoming Support Ticket",
                        description=message.content if message.content else "*[No Text Provided]*",
                        color=discord.Color.orange()
                    )
                    embed.set_author(name=f"{message.author.display_name} (@{message.author.name})", icon_url=message.author.avatar.url if message.author.avatar else None)
                    embed.set_footer(text=f"User ID: {message.author.id} • Forwarded Automatically")
                    
                    # Handle any file/image attachments they might have uploaded in the DM
                    if message.attachments:
                        embed.add_field(name="Attachments", value=f"📎 Sent {len(message.attachments)} file(s)", inline=False)
                    
                    await owner.send(embed=embed)
            except Exception as e:
                print(f"Failed to route ticket message to owner DMs: {e}")

    # -------------------------------------------------------------
    # Administrative Command: /viewservers
    # -------------------------------------------------------------
    @app_commands.command(name="viewservers", description="[Admin Only] View all servers this bot is active in")
    async def view_servers(self, interaction: discord.Interaction):
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ This administrative tool is restricted.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        guild_list = []
        for guild in self.bot.guilds:
            guild_list.append(f"• **{guild.name}** *(Members: {guild.member_count} | ID: {guild.id})*")
        
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
        if interaction.user.name != OWNER_USERNAME:
            return await interaction.response.send_message("❌ This administrative tool is restricted.", ephemeral=True)
        
        await interaction.response.defer(ephemeral=True)
        
        success_count = 0
        failed_count = 0

        embed = discord.Embed(
            title="📢 Global Broadcast Notification",
            description=message,
            color=discord.Color.gold()
        )
        embed.set_footer(text=f"Sent by Bot Administration • {interaction.user.display_name}")

        for guild in self.bot.guilds:
            target_channel = guild.system_channel or guild.rules_channel
            
            if not target_channel:
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
