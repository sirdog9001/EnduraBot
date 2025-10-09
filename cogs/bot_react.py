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


    # @commands.Cog.listener()
    # async def on_message(self, message: discord.Message):
    
    #     alert_channel_id = self.settings_data.get("alert_channel_id")
    #     sysop_role_id = self.settings_data.get("sysop_role_id")


    #     if message.channel.id == alert_channel_id:
    #         if any(role.id == sysop_role_id for role in message.role_mentions):
    #             try:
    #                 await message.delete()
    #                 await message.author.send(content="Please use the /alert command if you need SYS:OP help.")
    #             except discord.Forbidden:
    #                 await message.delete()
    #                 await message.channel.send()
    #     else:
    #         return

    #     await self.bot.process_commands(message)

async def setup(bot):
    await bot.add_cog(bot_react(bot))