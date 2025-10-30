import logging
from utils.logging_setup import INVITES
import datetime
from discord.ext import commands, tasks

logger = logging.getLogger('endurabot.' + __name__)

def find_invite_by_code(invite_list, code):
    for inv in invite_list:
        if inv.code == code:
            return inv

class invites_use(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, member):

        invites_before_join = self.bot.invites
        invites_after_join = await member.guild.invites()

        for invite in invites_before_join:
            if invite.uses < find_invite_by_code(invites_after_join, invite.code).uses:

                logger.log(INVITES, f"{member.name} ({member.id}) has joined with invite [{invite.code}] created by {invite.inviter} ({invite.inviter.id}) on {invite.created_at.strftime('%B %d, %Y')}.")

                self.bot.invites = invites_after_join

                return

async def setup(bot):
    await bot.add_cog(invites_use(bot))