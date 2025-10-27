import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
from discord import app_commands
from discord import app_commands, AllowedMentions
import logging
import datetime
import utils.config_loader as config_loader
from utils.config_loader import SETTINGS_DATA
from utils.permissions_checker import check_permissions
from classes.db_rgit_games_handler import DBRGITGames
from classes.itad_get_games_handler import ItadGameSearchHandler
from classes.itad_get_deals_handler import ItadGameDealsHandler

logger = logging.getLogger('endurabot.' + __name__)
db = DBRGITGames()

GUILD_ID = int(os.getenv('guild'))
API_TOKEN = os.getenv('itad-token')


class AddView(discord.ui.View):

    def __init__(self, game_title, game_id, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.title = game_title
        self.game_id = game_id

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green, emoji="✅")
    async def returnTrue(self, interaction: discord.Interaction, button):
        
        try:
            db.add_game(self.title, self.game_id, interaction.user.id)
        except ValueError:
            await interaction.response.send_message("Game already in table.", ephemeral=True)
            return
        except TypeError:
            await interaction.response.send_message("Access to API was rejected. Please notify Sirdog.", ephemeral=True)
            return
        except RuntimeError:
            await interaction.response.send_message("Due to technical limitations no more games may be added. Please notify Sirdog.", ephemeral=True)
            return
        except KeyError:
            await interaction.response.send_message("Game did not have all expected information. Please notify Sirdog.", ephemeral=True)
            return
        
        await interaction.response.send_message("Game added.", ephemeral=True)
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="🛑")
    async def returnFalse(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("Aborting...", ephemeral=True)
        self.stop()

async def addGamePrompt(interaction: discord.Interaction, title):
    
    try:
        
        itad_search = ItadGameSearchHandler(title)
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title=itad_search.get_title(),
            color=16777215 
            ) 
        embed.set_image(url=itad_search.get_boxart())
        embed.add_field(name="Released", value=datetime.datetime.strptime(itad_search.get_release_date(), '%Y-%m-%d').strftime('%B %d, %Y'), inline=False)
        embed.add_field(name="Publishers", value=', '.join(itad_search.get_publishers()), inline=False)
        embed.add_field(name="Tags", value=', '.join(itad_search.get_tags()), inline=False)
        #embed.set_footer(text="Powered by the IsThereAnyDeal API")

        view = AddView(game_title=itad_search.get_title(), game_id=itad_search.get_id())
        await interaction.followup.send(content="Is this the game you wish to add?", embed=embed, view=view, ephemeral=True)
        await view.wait()
    
    except ValueError:
        await interaction.response.send_message("The game could not be found. Please try again. Please be *very* specific; special characters and capitalization *do* matter.", ephemeral=True)
        return
    
    except RuntimeError:
        await interaction.response.send_message("Due to character limits additional games may not be added. Please speak with Sirdog.")
        return

async def removeGame(interaction: discord.Interaction, title):
            
    rgit_game = ItadGameSearchHandler(title)
    rgit_games_db = DBRGITGames()
    await interaction.response.defer(ephemeral=True)

    if rgit_games_db.check_if_exists(rgit_game.get_id()) == False:
        await interaction.followup.send("The game is not in the database.", ephemeral=True)
        return
    
    rgit_games_db.remove_game(rgit_game.get_id())
    await interaction.followup.send("Game removed.", ephemeral=True)

class itad(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.variables_file = {}
        self.settings_data = SETTINGS_DATA
        self.settings_data_g = config_loader.SETTINGS_DATA
    
        self.default_allowed_mentions = AllowedMentions(
                everyone=False,
                users=True, 
                roles=True      
            )

 # --- /rgit-edit ---

    @app_commands.command(name="rgit-edit", description="Add or remove a game from the RGIT database.")
    @app_commands.check(check_permissions)
    @app_commands.choices(options = [
    app_commands.Choice(name="Add Game",value="add"),
    app_commands.Choice(name="Remove Game",value="remove")
])
    @app_commands.guilds(GUILD_ID)
    async def rgitedit(self, interaction: discord.Interaction, options: app_commands.Choice[str], title: str):

        
        if options.value == "add":
            
            await addGamePrompt(interaction, title)
        
        else:
            
           await removeGame(interaction, title)
           
 # --- /rgit-table ---

    @app_commands.command(name="rgit-list", description="List all games in the RGIT table.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def rgitlist(self, interaction: discord.Interaction):

        temporary_list = []
        db = DBRGITGames()

        for game in db.list_games():
            temporary_list.append(f"- {game}")
       
        games = "\n".join(temporary_list)
        embed = discord.Embed(title="Games List", description=games, color=3800852)
        embed.set_footer(text="Powered by the IsThereAnyDeal API")
        await interaction.response.send_message(content="The following is a list of embeds on the RGIT table.", embed=embed, ephemeral=True)


# --- /rgit-deals --

    @app_commands.command(name="rgit-deals", description="List all games in the RGIT table.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def rgitdeals(self, interaction: discord.Interaction):

        db = DBRGITGames()
        deals = ItadGameDealsHandler(db.get_ids())
        name_to_id_dict = db.get_ids_and_names()
        price_format = 12345.6789

        embed = discord.Embed(title="Available Deals", description="The following are all the deals currently available for the RGIT games.")

        for deal in deals.get_deals():        
            id = deal["id"]
            game_name = name_to_id_dict[id]
            deals_amount = "${:0.2f}".format(deal["deals"][0]["price"]["amount"])
            full_amount = "${:0.2f}".format(deal["deals"][0]["regular"]["amount"])
            
            #{deal["deals"][0]["price"]["amount"].format(price_format)}

            embed.add_field(name=f"{game_name} ({deal["deals"][0]["cut"]}% Off)", value=f"{deals_amount} ({full_amount}) at [{deal["deals"][0]["shop"]["name"]}]({deal["deals"][0]["url"]})")

        embed.set_footer(text="Powered by the IsThereAnyDeal API.")
        await interaction.response.send_message(embed=embed)
        
async def setup(bot):
    await bot.add_cog(itad(bot))