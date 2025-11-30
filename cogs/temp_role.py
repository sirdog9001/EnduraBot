import os
from dotenv import load_dotenv

load_dotenv()

import discord
import datetime
from datetime import timedelta
from discord.ext import commands
from discord import app_commands, AllowedMentions
import logging
import utils.config_loader as config_loader
from utils.config_loader import SETTINGS_DATA, MISC_DATA
from classes.db_trole_handler import DBTempRole
from utils.logging_setup import UNAUTHORIZED
from utils.permissions_checker import check_permissions

logger = logging.getLogger('endurabot.' + __name__)

GUILD_ID = int(os.getenv('guild'))

db_temp_role = DBTempRole()

class temp_role(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
        self.settings_data = SETTINGS_DATA
        self.misc_data = MISC_DATA
        self.settings_data_g = config_loader.SETTINGS_DATA
        self.misc_data_g = config_loader.MISC_DATA

        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True,
                roles=True
            )

    role_list = SETTINGS_DATA["mod_editable_roles"]
    options_list = []
    for role_name, role_id in role_list.items():
        #Because role ID numbers are so long, it's interpreted as being too big an integer and causes Discord to crash spectacularly.
        #So need to make it a string using an f-string.
        options_list.append(app_commands.Choice(name=role_name,value=f"{role_id}"))

    @app_commands.command(name="trole", description="Give a user a role temporarily.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.choices(roles=options_list)
    @app_commands.describe(
        target = "Who is the target?",
        length = "Length, in hours, the L should last for. (default: 24)",
        roles = f"Which role should be given to the target? (default: {options_list[0].name})",
        check = "If true, will be told if there's an active timer for the target. Nothing else will happen."
    )
    async def trole(self, interaction: discord.Interaction, target: discord.Member, roles: str = options_list[0].value, length: int = 24, check: bool = False):

        role = interaction.guild.get_role(int(roles))
        timestamp_equation = datetime.datetime.now() + timedelta(minutes=length)
        timestamp = timestamp_equation.replace(microsecond=0)
        timestamp_fancy = timestamp.strftime("%B %d, %Y %H:%M")
        epoch = round(timestamp_equation.timestamp())

        if check == True:
            if db_temp_role.check_status(target.id) == False:
                await interaction.response.send_message(f"<@{target.id}> does not have a temporary role.", ephemeral=True)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) checked if {target.name} ({target.id}) has a temporary role. [FALSE]")
                return
            else:
                timestamp = db_temp_role.check_time(target.id)
                mod_id =  db_temp_role.get_mod(target.id)
                role_id = db_temp_role.get_role(target.id)
                await interaction.response.send_message(f"<@{mod_id}> gave <@&{role_id}> to <@{target.id}>. It is set to be removed <t:{timestamp}:f> (<t:{timestamp}:R>)", ephemeral=True)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) checked if {target.name} ({target.id}) has a temporary role. [TRUE][@{role.name}]")
                return

        if target.bot:
            await interaction.response.send_message("Bots may not be given a temporary role.", ephemeral=True)
            logger.log(UNAUTHORIZED, f"{interaction.user.name} ({interaction.user.id}) tried to give a temporary role to bot {target.name} ({target.id}).")
            return

        if length <= 0:
            await interaction.response.send_message("Hilarious.", ephemeral=True)
            return

        db_temp_role.add_user(target.id, target.name, interaction.user.id, interaction.user.name, roles, timestamp)

        if not role in target.roles:
            await target.add_roles(role)

        if target.voice:
            await target.move_to(None)

        embed_executor = discord.Embed(
            title=":regional_indicator_l: Action successful.",
            description=f"<@{target.id}> given <@&{roles}>. **Please read the information below carefully**. \n\n- If you would like to remove the role early, simply remove the role using any available method. It will be handled gracefully.\n- If you want to *give the role back* after *already* removing it early, again, simply use any available method. The original scheduled removal time will stand.\n- If you want to *change when the scheduled removal is*, run the command again. Be aware this will attempt to send another DM to <@{target.id}>.\n\n If the notification sent field below is :x: then attempting to DM them failed — likely due to their settings. You will need to notify them manually.",
            color=3800852)
        embed_executor.add_field(name="Automatic Removal Time", value=f"<t:{epoch}:f> (<t:{epoch}:R>)", inline=False)

        try:
            embed_notification = discord.Embed(
            title="You have been given a role temporarily.",
            description=f"<@{interaction.user.id}> has given you the role `@{role.name}` in the Endurance Coalition.\n\n If you were in a VC when they performed this action you may have experienced being disconnected suddenly; this is done to ensure that the restrictions that come with the role apply immediately.\n\n The date and time below is when the role will be removed automatically. It is at the discretion of staff as to whether it is removed early.",
            color=15277667)
            embed_notification.add_field(name="Automatic Removal Time", value=f"<t:{epoch}:f> (<t:{epoch}:R>)", inline=False)

            await target.send(embed=embed_notification)
            noti_success = ":white_check_mark:"
        except discord.Forbidden:
            noti_success = ":x:"

        logger.info(f"{interaction.user.name} ({interaction.user.id}) gave [@{role.name}] to {target.name} ({target.id}) for {length} hour(s). Removal scheduled for {timestamp_fancy}.")
        embed_executor.add_field(name="Notification Sent?", value=noti_success, inline=False)
        await interaction.response.send_message(embed=embed_executor, ephemeral=True)

async def setup(bot):
    await bot.add_cog(temp_role(bot))