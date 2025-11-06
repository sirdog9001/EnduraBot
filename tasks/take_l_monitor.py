import os
from discord.utils import get
import datetime
from datetime import datetime
from discord.ext import tasks, commands
import logging
from classes.db_takeL_handler import DBTakeL
from utils.config_loader import SETTINGS_DATA

logger = logging.getLogger("endurabot." + __name__)

take_l_db = DBTakeL()

GUILD_ID = int(os.getenv("guild"))


class take_l_monitor(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(GUILD_ID)
        self.settings_data = SETTINGS_DATA
        self.check_length_minutely.start()

    def cog_unload(self):
        self.check_length_minutely.cancel()

    @tasks.loop(minutes=1)
    async def check_length_minutely(self):

        timestamps = take_l_db.get_timestamps()

        for timestamp in timestamps:
            if datetime.now() > timestamp:
                user = self.guild.get_member(
                    take_l_db.get_user_id_by_timestamp(timestamp)
                )
                role = self.guild.get_role(self.settings_data.get("l_role_id"))
                if role in user.roles:
                    await user.remove_roles(role)
                    logger.info(
                        f"{take_l_db.get_user_name_by_timestamp(timestamp)} ({take_l_db.get_user_id_by_timestamp(timestamp)}) was given the L and it's duration has ended. Role removed and L-status removed from database."
                    )
                    take_l_db.remove_user_by_timestamp(timestamp)
                else:
                    logger.info(
                        f"{take_l_db.get_user_name_by_timestamp(timestamp)} ({take_l_db.get_user_id_by_timestamp(timestamp)}) was given the L and it's duration has ended. Role detected to have been removed early. Removed L-status from database."
                    )
                    take_l_db.remove_user_by_timestamp(timestamp)

    @check_length_minutely.before_loop
    async def before_daily_bible_quote(self):
        await self.bot.wait_until_ready()


async def setup(bot):
    await bot.add_cog(take_l_monitor(bot))
