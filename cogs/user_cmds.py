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

class user_cmds(commands.Cog):
    
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


    # --- COMMAND: /info ---


    @app_commands.command(name="info", description="Get information on a server member.")
    @app_commands.guilds(GUILD_ID)
    async def info(self, interaction: discord.Interaction, user: discord.Member):
        
        create_epoch = round(user.created_at.timestamp()) #Get UNIX timestamp for when the member's account was created.
        join_epoch = round(user.joined_at.timestamp()) #Get UNIX timestamp for when member joined the Discord.
        role_ids = [f"<@&{role.id}>" for role in user.roles if role.name != "@everyone"] #Get list of all role IDs the user has, excluding the default @@everyone role.
        sysop_role_id = self.settings_data.get("sysop_role_id") #Get SYSOP role ID from JSON.
        mod_role_id = self.settings_data.get("mod_role_id") #Get mod role ID from JSON.
        admin_role_id = self.settings_data.get("admin_role_id") #Get admin role ID from JSON.

        guild_sysop_role = discord.utils.get(interaction.guild.roles, id=sysop_role_id)
        guild_admin_role = discord.utils.get(interaction.guild.roles, id=admin_role_id)
        guild_mod_role = discord.utils.get(interaction.guild.roles, id=mod_role_id)

        if guild_sysop_role in user.roles:
            is_sysop = ":white_check_mark:"
        else:
            is_sysop= ":x:"

        if guild_admin_role in user.roles or guild_mod_role in user.roles:
            is_staff = ":white_check_mark:"
        else:
            is_staff = ":x:"

        embed = discord.Embed(title=f"Information on {user.name}.", color=discord.Color.green())
        embed.set_thumbnail(url=user.display_avatar.url)
        embed.add_field(name="Identity", value=f"{user.mention} ({user.id})", inline=False)
        embed.add_field(name="Account Created", value=f"<t:{create_epoch}:f> (<t:{create_epoch}:R>)", inline=False)
        embed.add_field(name="Joined", value=f"<t:{join_epoch}:f> (<t:{join_epoch}:R>)", inline=False)
        embed.add_field(name="Backend Operator?", value=is_sysop)
        embed.add_field(name="Server Staff?", value=is_staff)
        
        if len(user.roles) - 1 == 1: #We do -1 to exclude @@everyone.
            embed.add_field(name="Roles", value="None", inline=False)
        else:
            embed.add_field(name="Roles", value=' | '.join(role_ids), inline=False)
            
        
        await interaction.response.send_message(embed=embed, ephemeral=True)


    # --- COMMAND: /about ---


    @app_commands.command(name="about", description="Get information about EnduraBot.")
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

        await interaction.response.send_message(embed=embed)


    # --- COMMAND: /alert ---


    @app_commands.command(name="alert", description="Submit a pinged alert to systems operators of a service being down.")
    @app_commands.guilds(GUILD_ID)
    
    async def alert(self, interaction: discord.Interaction, desc: str):

        sailor_role_id = self.settings_data.get("sailor_role_id") #Get mod role ID from JSON.
        sysop_role_id = self.settings_data.get("sysop_role_id")
        alert_channel_id = self.settings_data.get("alert_channel_id")
        guild_sailor_role = discord.utils.get(interaction.guild.roles, id=sailor_role_id)
        guild_alert_channel = self.bot.get_channel(alert_channel_id)
        sysop_role = interaction.guild.get_role(sysop_role_id)
        

        # Only allow sailors to use this command.
        if not guild_sailor_role in interaction.user.roles:
            await interaction.response.send_message(content="Access denied.", ephemeral=True)
            return
        
        await interaction.response.send_message(content="Your report has been submitted.", ephemeral=True)
        await guild_alert_channel.send(
            content=f"# :rotating_light: INCIDENT ALERT :rotating_light:\n\n **Attention**: {sysop_role.mention}\n\n **Reporting User**: {interaction.user.mention} (from <#{interaction.channel.id}>) \n\n **Details**: \"{desc}\" \n\n Systems operator investigation requested! Please post in this channel and notify {interaction.user.mention} when investigation begins.", 
            allowed_mentions=self.default_allowed_mentions
            )

    # --- COMMAND: /estop ---

    @app_commands.command(name="estop", description="Perform an emergency shutdown of EnduraBot.")
    @app_commands.guilds(GUILD_ID)

    async def estop(self, interaction: discord.Interaction):

        guild_alert_channel = self.bot.get_channel(self.settings_data.get("alert_channel_id"))
        sysop_role_id = interaction.guild.get_role(self.settings_data.get("sysop_role_id"))

        eligible_roles = [
            discord.utils.get(interaction.guild.roles, id=self.settings_data.get("sysop_role_id")),
            discord.utils.get(interaction.guild.roles, id=self.settings_data.get("mod_role_id")),
            discord.utils.get(interaction.guild.roles, id=self.settings_data.get("admin_role_id"))
        ]

        if not set(eligible_roles).intersection(interaction.user.roles):
            await interaction.response.send_message("Access denied.", ephemeral=True)
            return
        
        await interaction.response.send_message(content=f"Emergency stop has been activated. Report sent to <#{guild_alert_channel.id}>.", ephemeral=True)
        await guild_alert_channel.send(
            content=f"# :warning: Emergency Stop Activation\n\n{sysop_role_id.mention}\n\n {interaction.user.mention} activated EnduraBot's **emergency stop** at this time. Please speak with them for details.\n\n EnduraBot will need to be manually rebooted in Portainer.", 
            allowed_mentions=self.default_allowed_mentions
            )
        
        logger.critical(f"Emergency stop activated by {interaction.user.name}. Shutting down...")
        await self.bot.close()

# --- COMMAND: /links ---

    @app_commands.command(name="links", description="Quick access to EDC relevant links.")
    @app_commands.guilds(GUILD_ID)
    async def links(self, interaction: discord.Interaction):

        links_list = self.settings_data.get("edc_links", {})

        embed = discord.Embed(
            title="Endurance Coalition Links List",
            color=discord.Color.purple()
        )

        for url, description in links_list.items():
            embed.add_field(
                name=description,
                value=url,
                inline=False
            )
        
        await interaction.response.send_message(embed=embed)

        return
        
async def setup(bot):
    await bot.add_cog(user_cmds(bot))