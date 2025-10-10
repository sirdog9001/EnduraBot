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
VERSION = os.getenv('version')

VARIABLES_FILE = "data/variables.json"

class manage_role(commands.Cog):
    
    # --- Initialize class ---

    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
    
        # Allow EnduraBot in this cog to ping roles and users.
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,  # Don't ping @everyone or @here by default
                users=True,      # Allow user mentions (like interaction.user.mention)
                roles=True       # Explicitly allow role mentions to trigger pings
            )
        
    # --- Load JSON ---

        try:
            with open(VARIABLES_FILE, 'r') as file_object:
                self.settings_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
            return


    # --- COMMAND: /roachcock ---


    @app_commands.command(name="roachcock", description="Give or revoke the Roach Cock role from a user.")
    @app_commands.guilds(GUILD_ID)
    async def roachcock(self, interaction: discord.Interaction, user: discord.Member):
        mod_role_id = self.settings_data.get("mod_role_id") #Get mod role ID from JSON.
        admin_role_id = self.settings_data.get("admin_role_id") #Get admin role ID from JSON.
        roach_cock_role_id = self.settings_data.get("roach_cock_role_id") #Get roach cock role ID from JSON.

        guild_cock_role = discord.utils.get(interaction.guild.roles, id=roach_cock_role_id) #user.remove_roles and vice versa need a discord.Role object, not just the ID.
        guild_admin_role = discord.utils.get(interaction.guild.roles, id=admin_role_id)
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=mod_role_id)

        has_permission = False
        
        if guild_admin_role in interaction.user.roles:
            has_permission = True

        if guild_mod_role in interaction.user.roles:
            has_permission = True

        if not has_permission:
            await interaction.response.send_message(
                "Access denied.",
                ephemeral=True
            )
            return
        
        # Let the magic happen, baby.
        if guild_cock_role in user.roles:
            await user.remove_roles(guild_cock_role)
            await interaction.response.send_message(f"{user.mention}, you have been spared from your roachy fate by {interaction.user.mention}. Be eternally grateful.", allowed_mentions=self.default_allowed_mentions)
        else:
            await user.add_roles(guild_cock_role)
            await interaction.response.send_message(f"{user.mention}, you have been cursed with the ROACH COCK by {interaction.user.mention}. You probably deserved it. :cockroach:", allowed_mentions=self.default_allowed_mentions)
        

    # --- COMMAND: /takel ---


    @app_commands.command(name="takel", description="Give or revoke the L role from a user.")
    @app_commands.guilds(GUILD_ID)
    async def takel(self, interaction: discord.Interaction, user: discord.Member):
        mod_role_id = self.settings_data.get("mod_role_id") #Get mod role ID from JSON.
        admin_role_id = self.settings_data.get("admin_role_id") #Get admin role ID from JSON.
        L_role_id = self.settings_data.get("L_role_id") #Get L role ID from JSON.

        guild_L_role = discord.utils.get(interaction.guild.roles, id=L_role_id) #user.remove_roles and vice versa need a discord.Role object, not just the ID.

        guild_admin_role = discord.utils.get(interaction.guild.roles, id=admin_role_id)
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=mod_role_id)

        has_permission = False
        
        if guild_admin_role in interaction.user.roles:
            has_permission = True

        if guild_mod_role in interaction.user.roles:
            has_permission = True

        if not has_permission:
            await interaction.response.send_message(
                "Access denied.",
                ephemeral=True
            )
            return
        
        # Let the magic happen, baby.
        if guild_L_role in user.roles:
            await user.remove_roles(guild_L_role)
            await interaction.response.send_message(f"{user.mention}, you have been spared from your :regional_indicator_l: fate by {interaction.user.mention}. Be eternally grateful.", allowed_mentions=self.default_allowed_mentions)
        else:
            await user.add_roles(guild_L_role)
            await interaction.response.send_message(f"{user.mention}, I'm gonna need you to take this :regional_indicator_l: given to you by {interaction.user.mention}. I'm disappointed in you.", allowed_mentions=self.default_allowed_mentions)
        

async def setup(bot):
    await bot.add_cog(manage_role(bot))