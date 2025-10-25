import discord
import logging
from utils.config_loader import PERMS_DATA

logger = logging.getLogger('endurabot.' + __name__)

async def check_permissions(interaction: discord.Interaction):

    cmd = interaction.command.name
    eligible_role_ids = PERMS_DATA.get(cmd, [])

    # If no IDs exist, then the command doesn't have a restriction.
    if not eligible_role_ids:
        return True
    
    eligible_roles_objects = []
    for role_id in eligible_role_ids:
        role = interaction.guild.get_role(role_id)
        if role:
            eligible_roles_objects.append(role)

    user_roles = interaction.user.roles

    if set(eligible_roles_objects).intersection(user_roles):
        return True
    elif not set(eligible_roles_objects).intersection(user_roles) and interaction.user.guild_permissions.administrator:
        logger.debug(f"Administrator {interaction.user.name} ({interaction.user.id}) bypassed traditional restrictions for command /{interaction.command.name}.")
        return True
    else:
        return False
        
