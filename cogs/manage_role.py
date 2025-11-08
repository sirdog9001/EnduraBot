import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands, AllowedMentions
import logging
from utils.config_loader import SETTINGS_DATA
from utils.logging_setup import UNAUTHORIZED
from utils.permissions_checker import check_permissions

logger = logging.getLogger('endurabot.' + __name__)

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
    role_list = SETTINGS_DATA["mod_editable_roles"]
    options_list = []
    for role_name, role_id in role_list.items():
        #Because role ID numbers are so long, it's interpreted as being too big an integer and causes Discord to crash spectacularly. 
        #So need to make it a string using an f-string.
        options_list.append(app_commands.Choice(name=role_name,value=f"{role_id}"))

    @app_commands.command(name="editrole", description="Give or revoke roles.")
    @app_commands.check(check_permissions)
    @app_commands.choices(options=options_list)
    @app_commands.guilds(GUILD_ID)
    async def editrole(self, interaction: discord.Interaction, user: discord.Member, options: app_commands.Choice[str], ping: bool = False):

        # And now we make it an integer for the "get_role" method.
        role = interaction.guild.get_role(int(options.value))

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
                logger.info(f"{interaction.user.name} ({interaction.user.id}) removed @{role.name} ({role.id}) from {user.name} ({user.id}). Ping: [TRUE]")
            else:
                await interaction.response.send_message(embed=embed)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) removed @{role.name} ({role.id}) from {user.name} ({user.id}). Ping: [FALSE]")

        else:

            await user.add_roles(role)
            embed = discord.Embed(
                title="🟢 Role Added",
                description=f"{role.mention} has been successfully added to {user.mention}.",
                color=3800852 
                )
            
            if ping == True:    
                await interaction.response.send_message(embed=embed, content=f"{user.mention}", allowed_mentions=self.default_allowed_mentions)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) added @{role.name} ({role.id}) to {user.name} ({user.id}). Ping: [TRUE]")
            else:
                await interaction.response.send_message(embed=embed)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) added @{role.name} ({role.id}) to {user.name} ({user.id}). Ping: [FALSE]")
        
async def setup(bot):
    await bot.add_cog(manage_role(bot))