import discord
from discord.ext import commands
from discord import AllowedMentions
import logging
import random
from config_loader import SETTINGS_DATA, MISC_DATA

logger = logging.getLogger('endurabot.' + __name__)

class bot_react(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_data = SETTINGS_DATA
        self.misc_data = MISC_DATA        
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True, 
                roles=True      
            )

    # Check if a message triggers advising the user to make an alert instead.
    
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
            logger.info(f"{message.author.name} ({message.author.id}) triggered the /alert filter. Content: [{message.content}]")
            await message.channel.send(embed=embed)
        else:
            return
        
    # Check if user should be insulted ;)

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):

        chance = SETTINGS_DATA["bot_insult_chance"]

        if self.bot.user.mentioned_in(message):

            value = random.random()

            if value <= chance:
                random_insult = random.choice(MISC_DATA["bot_insults"])
                await message.channel.send(f"{message.author.mention}, {random_insult}", allowed_mentions=self.default_allowed_mentions)
            else:
                return
            
            

async def setup(bot):
    await bot.add_cog(bot_react(bot))