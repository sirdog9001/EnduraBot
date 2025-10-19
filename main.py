import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

import discord
from discord.ext import commands

# Setup logging
import logging_setup
logger = logging_setup.configure_logging()

# Environment variable stuff
BOT_TOKEN= os.getenv('bot_token')
GUILD_ID = int(os.getenv('guild'))

guild_object = discord.Object(id=GUILD_ID)
whitelisted_guild_ids_str = os.getenv('guilds')

# Intents
intents = discord.Intents.default()
intents.members = True         
intents.presences = True        
intents.message_content = True 

bot = commands.Bot(command_prefix='!', intents=intents)
bot.initial_start_time = None

@bot.event
async def on_guild_join(guild):
    if guild.id != GUILD_ID:
        await guild.leave()
        logger.warning(f"Bot joined unauthorized guild '{guild.name}' (ID: {guild.id}). Leaving...")
        return
    else:
        logger.info(f"Bot joined authorized guild '{guild.name}' (ID: {guild.id}).")

@bot.event
async def on_ready():

    # Load cogs.
    try:
        for filename in os.listdir("cogs"):
            if filename.endswith(".py"):
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded cogs.{filename[:-3]}")
    except Exception as e:
        logger.critical("FATAL ERROR: ", e)    
    
    # Sync slash commands to relevant guild.
    try:
        synced = await bot.tree.sync(guild=guild_object)
        logger.info(f"Synced {len(synced)} commands.")
    except Exception as e:
        logger.critical("FATAL ERROR: ", e)    

    logger.info("Hello, world! I am awake and ready to work!")
    
    if bot.initial_start_time == None:
        bot.initial_start_time = round(discord.utils.utcnow().timestamp())

bot.run(BOT_TOKEN)


