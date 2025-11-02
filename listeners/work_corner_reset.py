import logging
import discord
import asyncio
from utils.config_loader import SETTINGS_DATA
from discord.ext import commands, tasks

logger = logging.getLogger('endurabot.' + __name__)

class work_corner_reset(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.settings_data = SETTINGS_DATA

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        vc = self.bot.get_channel(self.settings_data.get("working_corner_vc_id"))
        vc_dname = self.settings_data.get("working_corner_default_name")

        if before.channel == vc and not vc.members and not vc.name == vc_dname:
            await vc.edit(name=vc_dname)
            logger.info(f"Working corner VC name reset as it has emptied.")

async def setup(bot):
    await bot.add_cog(work_corner_reset(bot))