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

    cog_instance = interaction.client.get_cog('rquote')

    user_role_ids = {role.id for role in interaction.user.roles}

    if not cog_instance.exempt_role_ids.isdisjoint(user_role_ids):
        return None
    
    return app_commands.Cooldown(1, cog_instance.cooldown)

class rquote(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True, 
                roles=True      
            )
        
        try:
            with open(VARIABLES_FILE, 'r') as file_object:
                self.settings_data = json.load(file_object)
                self.exempt_role_ids = set(self.settings_data.get("cooldown_exempt_roles"))
                self.cooldown = self.settings_data.get("rquote_cooldown_in_minutes")
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


    # --- COMMAND: /rquote ---


    @app_commands.command(name="rquote", description="Take an out of context quote and give it the wrong context.")
    @app_commands.guilds(GUILD_ID)
    @app_commands.checks.dynamic_cooldown(custom_cooldown)

    async def rquote(self, interaction: discord.Interaction):
        
        ooc_channel_id = self.settings_data.get("out_of_context_channel_id")
        ooc_channel = self.bot.get_channel(ooc_channel_id)

        if interaction.channel.id == ooc_channel_id:
            await interaction.response.send_message("You may not generate quotes in the channel quotes come from.", ephemeral=True)
            return

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


        # Select a random theme.
        selected_theme = random.choice(['hr', 'court', 'dating'])

        # --- HUMAN RESOURCES THEME ---
        if selected_theme == 'hr': 

            random_opener = random.choice(self.misc_data["ooc_hr"])

            embed = discord.Embed(
                title="💼 HR Office of EDC, Inc.", 
                description=f"{random_opener}\n\n>>> {formatted_quote}",
                color=discord.Color.purple()
                )
            embed.set_footer(text="This scenario is not representative of the Endurance Coalition's values.")
            await interaction.response.send_message(embed=embed)
       
        # --- DATING THEME ---
        elif selected_theme == 'dating':

            random_opener = random.choice(self.misc_data["ooc_dating"])

            embed = discord.Embed(
                title="❤️‍🔥 A Love Story", 
                description=f"{random_opener}\n\n>>> {formatted_quote}",
                color=discord.Color.pink()
                )
            embed.set_footer(text="This scenario is not representative of the Endurance Coalition's values.")
            await interaction.response.send_message(embed=embed)

        # --- COURT THEME ---
        elif selected_theme == 'court':

            random_opener = random.choice(self.misc_data["ooc_court"])

            embed = discord.Embed(
                title="⚖️ EDC Court of Appeals", 
                description=f"{random_opener}\n\n>>> {formatted_quote}",
                color=15086336
                )
            embed.set_footer(text="This scenario is not representative of the Endurance Coalition's values.")
            await interaction.response.send_message(embed=embed)

    @rquote.error
    async def rquote_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            minutes, seconds = divmod(int(error.retry_after), 60)
            if minutes > 0:
                await interaction.response.send_message(f"This command is on cooldown. Try again in {minutes} minute(s) and {seconds} second(s).", ephemeral=True)
            else:
                await interaction.response.send_message(f"This command is on cooldown. Try again in {seconds} second(s).", ephemeral=True)

async def setup(bot):
    await bot.add_cog(rquote(bot))