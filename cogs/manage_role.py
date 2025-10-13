import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands, AllowedMentions
import random
import json
import re
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

GUILD_ID = int(os.getenv('guild'))

VARIABLES_FILE = "data/variables.json"

class manage_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True, 
                roles=True      
            )

        try:
            with open(VARIABLES_FILE, 'r') as file_object:
                self.settings_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
            return    


    # --- COMMAND: /editrole ---


    @app_commands.command(name="editrole", description="Give or revoke roles.")
    @app_commands.guilds(GUILD_ID)
    async def editrole(self, interaction: discord.Interaction, user: discord.Member, role: discord.Role):
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("mod_role_id"))
        guild_admin_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("admin_role_id"))

        # If not a moderator or administrator, reject.
        if not guild_mod_role in interaction.user.roles and not guild_admin_role in interaction.user.roles:
            await interaction.response.send_message("Access denied.", ephemeral=True)
            return

        # If the role is not editable AND the executor is not an administrator, reject. If an administrator, approve.
        if role.id not in self.settings_data.get("mod_editable_roles").values() and not guild_admin_role in interaction.user.roles:
            await interaction.response.send_message("You do not have permission to edit this role.", ephemeral=True)
            return
        
        # Disallow messing with the admin or mod roles for security reasons.
        if role == guild_mod_role or role == guild_admin_role:
            await interaction.response.send_message("Adjusting the mod or admin roles with EnduraBot is restricted for security purposes.", ephemeral=True)
            return
        
        # Change roles.
        if role in user.roles:
            await user.remove_roles(role)
            await interaction.response.send_message(f"{user.mention} role **@{role.name}** has been removed.", allowed_mentions=self.default_allowed_mentions)
        else:
            await user.add_roles(role)
            await interaction.response.send_message(f"{user.mention} role **@{role.name}** has been added.", allowed_mentions=self.default_allowed_mentions)
        
async def setup(bot):
    await bot.add_cog(manage_role(bot))