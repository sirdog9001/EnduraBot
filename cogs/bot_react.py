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
logger.setLevel(logging.DEBUG)

GUILD_ID = int(os.getenv('guild'))

VARIABLES_FILE = "data/variables.json"
MISC_FILE = "data/misc_text.json"

class bot_react(commands.Cog):
 # --- Initialize class ---

    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,  # Don't ping @everyone or @here by default
                users=True,      # Allow user mentions (like interaction.user.mention)
                roles=True       # Explicitly allow role mentions to trigger pings
            )
        
        # Load the variables.json file.
        try:
            with open(VARIABLES_FILE, 'r') as file_object:
                self.settings_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
            return
        
        try:
            with open(MISC_FILE, 'r') as file_object:
                self.misc_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully miscellaneous text from {MISC_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {MISC_FILE} not found.")
            return


    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
    
        sysop_role_id = self.settings_data.get("sysop_role_id")
        identifiers = self.misc_data.get("issue_identifiers", [])
        servers = self.misc_data.get("server_identifiers", [])

        if not any(role.id == sysop_role_id for role in message.role_mentions):
            return
        
        if any(role.id == sysop_role_id for role in message.author.roles):
           return
        
        if message.author.bot:
            return

        if any(servers in message.content.lower() for servers in servers) and any(identifiers in message.content.lower() for identifiers in identifiers):
            await message.delete()
            embed = discord.Embed(
                title="⚙️ Having an issue? Use `/alert`!", 
                description="An **automated filter** has detected that a recent ping was made to systems operators in relation to an issue with EDC services.\n\n The preferred method of reporting a service being down is `/alert`.",
                color=8650752
            )
            await message.channel.send(embed=embed)
        else:
            return

async def setup(bot):
    await bot.add_cog(bot_react(bot))