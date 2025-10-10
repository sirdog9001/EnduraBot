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
GOSPELS_FILE = "data/bible_gospels.json"

class bible(commands.Cog):
    
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
        
    # --- Load JSON files ---

        # Settings
        try:
            with open(VARIABLES_FILE, 'r') as file_object:
                self.settings_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
            return
        
        # Bible gospels
        try:
            with open(GOSPELS_FILE, 'r') as file_object:
                self.gospels_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded gospel names from {GOSPELS_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {GOSPELS_FILE} not found.")
            return



    # --- COMMAND: /bibleq ---

    @app_commands.command(name="bibleq", description="Generate a totally legitimate Bible quote.")
    @app_commands.guilds(GUILD_ID)

    async def bibleq(self, interaction: discord.Interaction):
        
        ooc_channel_id = self.settings_data.get("out_of_context_channel_id")
        ooc_channel = self.bot.get_channel(ooc_channel_id)
        random_gospel = random.choice(self.gospels_data)
        fetch_limit = 100 # Going too far back would be resource intensive.

        if interaction.channel.id == ooc_channel_id:
            await interaction.response.send_message("You may not generate quotes in the channel quotes come from.", ephemeral=True)
            return

        msg_table = [
            msg async for msg in ooc_channel.history(limit=fetch_limit)
            if not msg.author.bot
            and ( 
                (msg.content and (
                    re.search(r'''["](.+?)["]''', msg.content)
                ))
            )
        ]

        selected_msg = random.choice(msg_table)

        match = re.search(r'''["](.+?)["]''', selected_msg.content) #Search for the quoted content
        extracted_quote = match.group(1).strip() if match else selected_msg.content.strip() #Strip everything that isn't the quoted content
        formatted_quote = f'"{extracted_quote}"' #Format the quoted content into quotations

        embed = discord.Embed(
            title="✝️ Bible Quote", 
            description=f"{formatted_quote}\n\n —**{random_gospel}**",
            color=discord.Color.purple()
            )
        embed.set_footer(text="This quote is not representative of the Endurance Coalition's values.")
        await interaction.response.send_message(embed=embed)


async def setup(bot):
    await bot.add_cog(bible(bot))