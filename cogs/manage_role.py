import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands, AllowedMentions
import logging
from config_loader import SETTINGS_DATA

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

GUILD_ID = int(os.getenv('guild'))

class manage_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_data = SETTINGS_DATA
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True, 
                roles=True      
            )


    # --- COMMAND: /editrole ---


    @app_commands.command(name="editrole", description="Give or revoke roles.")
    @app_commands.guilds(GUILD_ID)
    async def editrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role, ping: bool = False):
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("mod_role_id"))
        guild_admin_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("admin_role_id"))
    
        # If not a moderator or administrator, reject.
        if not guild_mod_role in interaction.user.roles and not guild_admin_role in interaction.user.roles:
            await interaction.response.send_message("Access denied.", ephemeral=True)
            return

        # If the role is not editable, reject.
        if role.id not in self.settings_data.get("mod_editable_roles").values():
            await interaction.response.send_message(f"{role.mention} is not on the approved list of editable roles.", ephemeral=True)
            return

        # Change roles.
        if role in user.roles:
            await user.remove_roles(role)

            embed = discord.Embed(
                title="⭕ Role Removed",
                description=f"{role.mention} has been successfully removed from {user.mention}.",
                color=8650752 
                )
            
            if ping == True:    
                await interaction.response.send_message(embed=embed, content=f"{user.mention}", allowed_mentions=self.default_allowed_mentions)
            else:
                await interaction.response.send_message(embed=embed)

        else:

            await user.add_roles(role)
            embed = discord.Embed(
                title="🟢 Role Added",
                description=f"{role.mention} has been successfully added to {user.mention}.",
                color=3800852 
                )
            
            if ping == True:    
                await interaction.response.send_message(embed=embed, content=f"{user.mention}", allowed_mentions=self.default_allowed_mentions)
            else:
                await interaction.response.send_message(embed=embed)
        
async def setup(bot):
    await bot.add_cog(manage_role(bot))