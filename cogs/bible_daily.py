import os
from dotenv import load_dotenv

load_dotenv()

import discord
from datetime import datetime, time, timezone, timedelta
from discord.ext import tasks, commands
import json
import logging
import random
import re

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

GUILD_ID = int(os.getenv('guild'))

VARIABLES_FILE = "data/variables.json"
MISC_FILE = "data/misc_text.json"

class bible_daily(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.daily_bible_quote.start()
        self.variables_file = {}

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
                logger.info(f"[{self.__class__.__name__}] Successfully loaded miscellaneous text from {MISC_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {MISC_FILE} not found.")
            return


    def cog_unload(self):
        self.daily_bible_quote.cancel()


    @tasks.loop(time=time(hour=16, minute=00, tzinfo=timezone.utc)) #Convert UTC to EST, so this should send at 12pm every day.
    async def daily_bible_quote(self):
        await self.bot.wait_until_ready()

        based_chat_channel = self.bot.get_channel(self.settings_data.get("based_chat_channel_id"))
        ooc_channel = self.bot.get_channel(self.settings_data.get("out_of_context_channel_id"))
        random_gospel = random.choice(self.misc_data["bible_gospels"])
        random_opener = random.choice(self.misc_data["daily_bible_openers"])

        # Current date - date roughly close to the first quote in #out-of-context
        num_days = datetime.now(timezone.utc) - datetime(2022, 3, 14, 0, 0, 0, tzinfo=timezone.utc)

        # This selects the random date.
        random_date = datetime.now(timezone.utc) - timedelta(days=random.randint(1, num_days.days))

        msg_table = [
            msg async for msg in ooc_channel.history(limit=75, around=random_date)
            if not msg.author.bot
            and ( 
                (msg.content and (
                    re.search(r'''["](.+?)["]''', msg.content)
                ))
            )
        ]

        # If a situation were to ever somehow occur where msg_table comes empty, use a pre-selected message to keep things moving.
        if not msg_table:
            selected_msg = await ooc_channel.fetch_message(1426039544490229811)
        else:       
            selected_msg = random.choice(msg_table)

        all_matches = re.findall(r'''["](.+?)["]''', selected_msg.content)
        
        extracted_quote = '"\n"'.join(match.strip() for match in all_matches)
        formatted_quote = f'"{extracted_quote}"'

        embed = discord.Embed(
            title="", 
            description=f"{formatted_quote}\n\n —**{random_gospel}**",
            color=discord.Color.purple()
            )
        embed.set_footer(text="This quote is not representative of the Endurance Coalition's values.")
        await based_chat_channel.send(content=f"# ✝️ Bible Quote of the Day\n\n:palms_up_together: {random_opener}", embed=embed)

    @daily_bible_quote.before_loop
    async def before_daily_bible_quote(self):
        logger.info("Waiting for bot to be ready before starting daily bible quote loop...")
        await self.bot.wait_until_ready()
        logger.info("Bot ready, starting daily bible quote loop.")

async def setup(bot):
    await bot.add_cog(bible_daily(bot))