import os
from dotenv import load_dotenv

load_dotenv()

import discord
import datetime
from datetime import timedelta
from discord.ext import commands
from discord import app_commands, AllowedMentions
import sys
import logging
import utils.config_loader as config_loader
from utils.config_loader import SETTINGS_DATA, MISC_DATA
from classes.db_takeL_handler import DBTakeL
from classes.db_monitor_handler import DBMonitor
from utils.logging_setup import UNAUTHORIZED
from utils.permissions_checker import check_permissions

logger = logging.getLogger('endurabot.' + __name__)

GUILD_ID = int(os.getenv('guild'))

take_l_db = DBTakeL()
monitor_db = DBMonitor()

class user_cmds(commands.Cog):
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

    # --- COMMAND: /user ---

    @app_commands.command(name="user", description="Get information on a server member.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(
        user = "Member to get information on."
    )
    async def user(self, interaction: discord.Interaction, user: discord.Member):

        create_epoch = round(user.created_at.timestamp()) #Get UNIX timestamp for when the member's account was created.
        join_epoch = round(user.joined_at.timestamp()) #Get UNIX timestamp for when member joined the Discord.
        role_ids = [f"<@&{role.id}>" for role in user.roles if role.name != "@everyone"] #Get list of all role IDs the user has, excluding the default @@everyone role.

        guild_sysop_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("sysop_role_id"))
        guild_admin_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("admin_role_id"))
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("mod_role_id"))

        if guild_sysop_role in user.roles:
            is_sysop = ":white_check_mark:"
        else:
            is_sysop= ":x:"

        if guild_admin_role in user.roles or guild_mod_role in user.roles:
            is_staff = ":white_check_mark:"
        else:
            is_staff = ":x:"

        if user.bot:
            bot_emoji = ":white_check_mark:"
        else:
            bot_emoji = ":x:"

        if user.premium_since == None:
            premium_emoji = ":x:"
        else:
            premium_emoji = ":white_check_mark:"

        embed = discord.Embed(title=f"Information on {user.name}.", color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Identity", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Global Name", value=user.global_name, inline=False)
        embed.add_field(name="Account Created", value=f"<t:{create_epoch}:f> (<t:{create_epoch}:R>)", inline=False)
        embed.add_field(name="Joined", value=f"<t:{join_epoch}:f> (<t:{join_epoch}:R>)", inline=False)
        embed.add_field(name="Backend Operator?", value=is_sysop)
        embed.add_field(name="Server Staff?", value=is_staff)
        embed.add_field(name="Bot?", value=bot_emoji)
        embed.add_field(name="Has Nitro?", value=premium_emoji)

        if len(user.roles) == 1: #We do -1 to exclude @@everyone.
            embed.add_field(name="Roles", value="None", inline=False)
        else:
            embed.add_field(name="Roles", value=' | '.join(role_ids), inline=False)

        await interaction.response.send_message(embed=embed, ephemeral=True)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) ran /user on {user.name} ({user.id}).")

    # --- COMMAND: /about ---

    @app_commands.command(name="about", description="Get information about EnduraBot.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def about(self, interaction: discord.Interaction):

        repo = self.settings_data.get("repo")
        version = self.settings_data.get("version")

        embed = discord.Embed(
            title="About me",
            description=f"Hello! My name is EnduraBot. I am a general purpose bot made for the Endurance Coalition. My creator is <@281589411962028034>.",
            color=discord.Color.blue()
                              )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(name="Version", value=version, inline=False)
        embed.add_field(name="GitHub Repository", value=repo, inline=False)
        embed.add_field(name="Uptime", value=f"<t:{self.bot.initial_start_time}:R>")

        await interaction.response.send_message(embed=embed)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) ran /about in #{interaction.channel.name} ({interaction.channel.id}).")

    # --- COMMAND: /alert ---

    @app_commands.command(name="alert", description="Submit a pinged alert to systems operators of a service being down.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(
        desc = "A brief description of the issue. Operators will see this."
    )
    async def alert(self, interaction: discord.Interaction, desc: str):

        guild_alert_channel = self.bot.get_channel(self.settings_data.get("alert_channel_id"))
        sysop_role = interaction.guild.get_role(self.settings_data.get("sysop_role_id"))

        await interaction.response.send_message(content="Your report has been submitted.", ephemeral=True)
        await guild_alert_channel.send(
            content=f"# :rotating_light: INCIDENT ALERT :rotating_light:\n\n **Attention**: {sysop_role.mention}\n\n **Reporting User**: {interaction.user.mention} (from <#{interaction.channel.id}>) \n\n **Details**: \"{desc}\" \n\n Systems operator investigation requested! Please post in this channel and notify {interaction.user.mention} when investigation begins.",
            allowed_mentions=self.default_allowed_mentions
            )

        logger.critical(f"{interaction.user.name} ({interaction.user.id}) submitted an alert to systems operators with the context: [{desc}].")

    # --- COMMAND: /estop ---

    @app_commands.command(name="estop", description="Perform an emergency shutdown of EnduraBot.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)

    async def estop(self, interaction: discord.Interaction):

        guild_alert_channel = self.bot.get_channel(self.settings_data.get("alert_channel_id"))
        sysop_role_id = interaction.guild.get_role(self.settings_data.get("sysop_role_id"))

        await interaction.response.send_message(content=f"Emergency stop has been activated. Report sent to <#{guild_alert_channel.id}>.", ephemeral=True)
        await guild_alert_channel.send(
            content=f"# :warning: Emergency Stop Activation\n\n{sysop_role_id.mention}\n\n {interaction.user.mention} activated EnduraBot's **emergency stop** at this time. Please speak with them for details.\n\n EnduraBot will need to be manually rebooted in Portainer.",
            allowed_mentions=self.default_allowed_mentions
            )

        logger.critical(f"Emergency stop activated by {interaction.user.name} ({interaction.user.id}). Shutting down...")
        await self.bot.close()

# --- COMMAND: /info ---

    @app_commands.command(name="info", description="Quick access to EDC relevant information.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.choices(options = [
        app_commands.Choice(name="Links",value="links"),
        app_commands.Choice(name="IP Addresses / Ports",value="ports")
])
    @app_commands.describe(
        options = "What information do you want?"
    )   
    async def info(self, interaction: discord.Interaction, options: app_commands.Choice[str]):

        if options.value == "links":

            links_list = self.settings_data.get("edc_links", {})

            embed = discord.Embed(
                title="Endurance Coalition Links",
                color=discord.Color.purple()
            )

            for url, description in links_list.items():
                embed.add_field(
                    name=description,
                    value=url,
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) ran /info and asked for LINKS in #{interaction.channel.name} ({interaction.channel.id}).")
            return

        if options.value == "ports":

            ports_list = self.settings_data.get("edc_ports", {})
            edc_ip = self.settings_data.get("edc_ip")
            edc_url = self.settings_data.get("edc_url")

            embed = discord.Embed(
                title="Endurance Coalition IP Addresses",
                description=f"Most games should accept `{edc_url}` as our IP address. Just append the port to the end like usual.\n\n If for some reason that does not work, our *raw* IP is `{edc_ip}`.",
                color=discord.Color.blue()
            )

            for game, port in ports_list.items():
                embed.add_field(
                    name=game,
                    value=port,
                    inline=False
                )

            await interaction.response.send_message(embed=embed)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) ran /info and asked for IP ADDRESSES / PORTS in #{interaction.channel.name} ({interaction.channel.id}).")
            return

# --- COMMAND: /reboot ---

    @app_commands.command(name="reboot", description="Reboot EnduraBot.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def reboot(self, interaction: discord.Interaction):

        logger.critical(f"{interaction.user.name} ({interaction.user.id}) rebooted me.")
        await interaction.response.send_message("Rebooting...", ephemeral=True)
        await self.bot.close()
        await os.execv(sys.executable, ['python'] + ['main.py'])

# --- COMMAND: /echo ---

    @app_commands.command(name="echo", description="Make EnduraBot speak.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def echo(self, interaction: discord.Interaction, msg: str):

        logger.info(f"{interaction.user.name} ({interaction.user.id}) sent a message as EnduraBot with content [{msg}].")
        await interaction.response.send_message("Message sent.", ephemeral=True)
        await interaction.channel.send(msg)

# --- COMMAND: /takeL ---

    @app_commands.command(name="takel", description="Give a user the L role for specified duration.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.describe(
        target = "Who gets the L?",
        length = "Length, in hours, the L should last for. (default: 24)",
        check = "If true, will be told if there's an active timer for the target. Nothing else will happen."
    )  
    async def takel(self, interaction: discord.Interaction, target: discord.Member, length: int = 24, check: bool = False):

        guild_l_role = discord.utils.get(interaction.guild.roles, id=self.settings_data.get("l_role_id"))
        timestamp_equation = datetime.datetime.now() + timedelta(hours=length)
        timestamp = timestamp_equation.replace(microsecond=0)
        timestamp_fancy = timestamp.strftime("%B %d, %Y %H:%M")
        epoch = round(timestamp_equation.timestamp())

        if check == True:
            if take_l_db.check_status(target.id) == False:
                await interaction.response.send_message(f"<@{target.id}> does not have the L.", ephemeral=True)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) checked if {target.name} ({target.id}) has the L. [FALSE]")
                return
            else:
                timestamp = take_l_db.check_time(target.id)
                mod_id =  take_l_db.get_mod(target.id)
                await interaction.response.send_message(f"<@{mod_id}> gave the L to <@{target.id}>. It is set to be removed <t:{timestamp}:f> (<t:{timestamp}:R>)", ephemeral=True)
                logger.info(f"{interaction.user.name} ({interaction.user.id}) checked if {target.name} ({target.id}) has the L. [TRUE]")
                return

        if target.bot:
            await interaction.response.send_message("Bots may not be given the L.", ephemeral=True) 
            logger.log(UNAUTHORIZED, f"{interaction.user.name} ({interaction.user.id}) tried to give the L to bot {target.name} ({target.id}).")
            return

        if length <= 0:
            await interaction.response.send_message("Hilarious.", ephemeral=True)
            return

        take_l_db.add_user(target.id, target.name, interaction.user.id, interaction.user.name, timestamp)

        if not guild_l_role in target.roles:
            await target.add_roles(guild_l_role)

        if target.voice:
            await target.move_to(None)

        embed_executor = discord.Embed(
            title=":regional_indicator_l: Action successful.",
            description=f"<@{target.id}> given the L. **Please read the information below carefully**. \n\n- If you would like to remove the L early, simply remove the role using any available method. It will be handled gracefully.\n- If you want to *give the L back* after *already* removing it early, again, simply use any available method. The original scheduled removal time will stand.\n- If you want to *change when the scheduled removal is*, run the command again. Be aware this will attempt to send another DM to <@{target.id}>.\n\n If the notification sent field below is :x: then attempting to DM them failed — likely due to their settings. You will need to notify them manually.",
            color=3800852)
        embed_executor.add_field(name="Automatic Removal Time", value=f"<t:{epoch}:f> (<t:{epoch}:R>)", inline=False)

        try:
            embed_notification = discord.Embed(
            title="You have been given the L.",
            description=f"<@{interaction.user.id}> has given you the L role in the Endurance Coalition.\n\n If you were in a VC when they performed this action you may have experienced being disconnected suddenly; this is done to ensure that the restrictions that come with the role apply immediately.\n\n The date and time below is when the role will be removed automatically. It is at the discretion of staff as to whether it is removed early.",
            color=15277667)
            embed_notification.add_field(name="Automatic Removal Time", value=f"<t:{epoch}:f> (<t:{epoch}:R>)", inline=False)

            await target.send(embed=embed_notification)
            noti_success = ":white_check_mark:"
        except discord.Forbidden:
            noti_success = ":x:"

        logger.info(f"{interaction.user.name} ({interaction.user.id}) gave the L to {target.name} ({target.id}) for {length} hour(s). Removal scheduled for {timestamp_fancy}.")
        embed_executor.add_field(name="Notification Sent?", value=noti_success, inline=False)
        await interaction.response.send_message(embed=embed_executor, ephemeral=True)

# --- COMMAND: /monitor ---

    @app_commands.command(name="monitor", description="Add someone to be monitored on join.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    @app_commands.choices(level = [
        app_commands.Choice(name="Ban and Send Alert",value="ban"),
        app_commands.Choice(name="Send Alert Only",value="alert")
])
    @app_commands.choices(action = [
        app_commands.Choice(name="Add",value="add"),
        app_commands.Choice(name="Remove",value="remove")
])
    @app_commands.describe(
        disc_id = "The Discord ID of the person to monitor for.",
        action = "What is being done?",
        level = "What should happen if the person joins?",
        name = "The common name of the person.",
        steam_id = "The STEAM ID of the person.",
        reason = "Why is the person being monitored?"
    )
    async def monitor(self, interaction: discord.Interaction, disc_id: str, action: app_commands.Choice[str], level: app_commands.Choice[str] = None, name: str = None, steam_id: str = None, reason: str = None):

        if action.value == "add":

            if monitor_db.check_status(int(disc_id)) == True:
                await interaction.response.send_message("Discord ID is already being monitored.", ephemeral=True)
                logger.error(f"{interaction.user.name} ({interaction.user.id}) attempted to add {monitor_db.get_name(int(disc_id))} ({disc_id}) when they are already being monitored.")
                return
            
            monitor_db.add_user(target_disc_id=disc_id, target_name=name, target_steam_id=steam_id, mod_name=f"{interaction.user.name}", mod_disc_id=f"{interaction.user.id}", reason=reason, level=level.value)
            await interaction.response.send_message("Entry successfully added.", ephemeral=True)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) added {name} (Discord: {disc_id} | Steam: {steam_id}) for monitoring at level [{level.value.upper()}]. Reason: [{reason}]")
            return
        
        if action.value == "remove":
            if monitor_db.check_status(int(disc_id)) == False:
                await interaction.response.send_message("Discord ID is already not being monitored.", ephemeral=True)
                logger.error(f"{interaction.user.name} ({interaction.user.id}) attempted to remove {disc_id} from monitoring but the ID wasn't found.")
                return
            
            await interaction.response.send_message("Entry successfully removed.", ephemeral=True)
            logger.info(f"{interaction.user.name} ({interaction.user.id}) removed {monitor_db.get_name(int(disc_id))} ({disc_id}) from monitoring.")
            monitor_db.remove_user(int(disc_id))
            return

async def setup(bot):
    await bot.add_cog(user_cmds(bot))