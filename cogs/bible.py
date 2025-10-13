import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands, AllowedMentions
from datetime import datetime, timezone, timedelta
import random
import json
import re
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

GUILD_ID = int(os.getenv('guild'))

VARIABLES_FILE = "data/variables.json"
MISC_FILE = "data/misc_text.json"


def custom_cooldown(interaction: discord.Interaction) -> app_commands.Cooldown | None:

    cog_instance = interaction.client.get_cog('bible')

    user_role_ids = {role.id for role in interaction.user.roles}

    if not cog_instance.exempt_role_ids.isdisjoint(user_role_ids):
        return None
    
    return app_commands.Cooldown(1, 1800)

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
                self.exempt_role_ids = set(self.settings_data.get("cooldown_exempt_roles"))
                logger.info(f"[{self.__class__.__name__}] Successfully loaded settings from {VARIABLES_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {VARIABLES_FILE} not found.")
            return
        
        # Bible gospels
        try:
            with open(MISC_FILE, 'r') as file_object:
                self.misc_data = json.load(file_object)
                logger.info(f"[{self.__class__.__name__}] Successfully loaded miscellaneous text from {MISC_FILE}")
        
        except FileNotFoundError:
            logger.critical(f"[{self.__class__.__name__}] FATAL ERROR: {MISC_FILE} not found.")
            return

    # --- COMMAND: /bibleq ---

    @app_commands.command(name="bibleq", description="Generate a totally legitimate Bible quote.")
    @app_commands.guilds(GUILD_ID)
    @app_commands.checks.dynamic_cooldown(custom_cooldown)

    async def bibleq(self, interaction: discord.Interaction):
        
        ooc_channel_id = self.settings_data.get("out_of_context_channel_id")
        ooc_channel = self.bot.get_channel(ooc_channel_id)
        random_gospel = random.choice(self.misc_data["bible_gospels"])

        if interaction.channel.id == ooc_channel_id:
            await interaction.response.send_message("You may not generate quotes in the channel quotes come from.", ephemeral=True)
            return

        # A date relatively close, but not too close, to the first OOC message.
        old_date = datetime(2022, 3, 14, 0, 0, 0, tzinfo=timezone.utc) 

        #Timezone declaration necessary to make this datetime object an 'aware' one.
        current_date = datetime.now(timezone.utc)

        num_days = current_date - old_date 

        random_date = current_date - timedelta(days=random.randint(1, num_days.days)) #This selects the random date.

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
            title="✝️ Bible Quote", 
            description=f"{formatted_quote}\n\n —**{random_gospel}**",
            color=discord.Color.purple()
            )
        embed.set_footer(text="This quote is not representative of the Endurance Coalition's values.")
        await interaction.response.send_message(embed=embed)

    @bibleq.error
    async def bibleq_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            minutes, seconds = divmod(int(error.retry_after), 60)
            if minutes > 0:
                await interaction.response.send_message(f"This command is on cooldown. Try again in {minutes} minute(s) and {seconds} second(s).", ephemeral=True)
            else:
                await interaction.response.send_message(f"This command is on cooldown. Try again in {seconds} second(s).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(bible(bot))