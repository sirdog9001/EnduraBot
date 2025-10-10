import os
from dotenv import load_dotenv

load_dotenv()

import discord
import datetime
from discord.ext import tasks, commands
from discord import AllowedMentions
import json
import logging
import random
import re

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

GUILD_ID = int(os.getenv('guild'))

VARIABLES_FILE = "data/variables.json"
GOSPELS_FILE = "data/bible_gospels.json"
OPENERS_FILE = "data/daily_bible_openers.json"

class bible_daily(commands.Cog):
        def __init__(self, bot):
            self.bot = bot
            self.daily_bible_quote.start()
            self.variables_file = {}

    # --- Load JSON files ---

            try:
                with open(VARIABLES_FILE, 'r') as file_object:
                    self.settings_data = json.load(file_object)
                    logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
            
            except FileNotFoundError:
                logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
                return
            
            try:
                with open(GOSPELS_FILE, 'r') as file_object:
                    self.gospels_data = json.load(file_object)
                    logger.info(f"[{self.__class__.__name__}] Successfully loaded gospel names from {GOSPELS_FILE}")
            
            except FileNotFoundError:
                logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {GOSPELS_FILE} not found.")
                return
            
            try:
                with open(OPENERS_FILE, 'r') as file_object:
                    self.openers_data = json.load(file_object)
                    logger.info(f"[{self.__class__.__name__}] Successfully loaded gospel openers from {OPENERS_FILE}")
            
            except FileNotFoundError:
                logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {OPENERS_FILE} not found.")
                return


        def cog_unload(self):
            self.daily_bible_quote.cancel()


        @tasks.loop(time=datetime.time(hour=16, minute=00, tzinfo=datetime.timezone.utc)) #Convert UTC to EST, so this should send at 12pm every day.
        async def daily_bible_quote(self):
            await self.bot.wait_until_ready()

            ooc_channel_id = self.settings_data.get("out_of_context_channel_id")
            based_chat_channel_id = self.settings_data.get("based_chat_channel_id")

            ooc_channel = self.bot.get_channel(ooc_channel_id)
            based_chat_channel = self.bot.get_channel(based_chat_channel_id)

            random_gospel = random.choice(self.gospels_data)
            random_opener = random.choice(self.openers_data)
            fetch_limit = 100 # Going too far back would be resource intensive.

            msg_table = [
                msg async for msg in ooc_channel.history(limit=fetch_limit)
                if not msg.author.bot # Not from a bot
                and ( # Start of combined OR condition
                    (msg.content and ( # Message has text AND CONTAINS a quoted string
                        re.search(r'''["](.+?)["]''', msg.content) # Checks if content CONTAINS "..."
                    ))
                )
            ]

            selected_msg = random.choice(msg_table)

            match = re.search(r'''["](.+?)["]''', selected_msg.content) #Search for the quoted content
            extracted_quote = match.group(1).strip() if match else selected_msg.content.strip() #Strip everything that isn't the quoted content
            formatted_quote = f'"{extracted_quote}"' #Format the quoted content into quotations

            embed = discord.Embed(
                title="✝️ Bible Quote of the Day", 
                description=f"{formatted_quote}\n\n —**{random_gospel}**",
                color=discord.Color.purple()
            )
            embed.set_footer(text="This quote is not representative of the Endurance Coalition's values.")

            await based_chat_channel.send(content=random_opener, embed=embed)     

        @daily_bible_quote.before_loop
        async def before_daily_bible_quote(self):
            logger.info("Waiting for bot to be ready before starting daily bible quote loop...")
            await self.bot.wait_until_ready()
            logger.info("Bot ready, starting daily bible quote loop.")

async def setup(bot):
    await bot.add_cog(bible_daily(bot))