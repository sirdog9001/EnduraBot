import os
from dotenv import load_dotenv

load_dotenv()

import discord
from discord.ext import commands
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
db = DBRGITGames() # Create connection to RGITGames DB.

GUILD_ID = int(os.getenv('guild'))
API_TOKEN = os.getenv('itad-token')

class AddView(discord.ui.View):

    # This class exists to 1) create the buttons at all and 2) assign functions that each button executes on press.

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
            logger.info(f"{interaction.user.name} ({interaction.user.id}) attempted to add already present game {self.title} to the RGIT table.")
            return
        except TypeError:
            await interaction.response.send_message("Access to API was rejected. Please notify Sirdog.", ephemeral=True)
            logger.error(f"{interaction.user.name} ({interaction.user.id}) got an API access rejection error.")
            return
        except RuntimeError:
            await interaction.response.send_message("Due to technical limitations no more games may be added. Please notify Sirdog.", ephemeral=True)
            logger.critical(f"{interaction.user.name} ({interaction.user.id}) attempted to exceed soft-limit of RGIT games. (P1)")
            return
        except KeyError:
            await interaction.response.send_message("Game did not have all expected information. Please notify Sirdog.", ephemeral=True)
            logger.error(f"{interaction.user.name} ({interaction.user.id}) attempted to add {self.title} ({self.game_id}) and the API did not give back all expected information.")
            return
        
        await interaction.response.send_message("Game added.", ephemeral=True)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) successfully adds {self.title} ({self.game_id}) to the RGIT table.")
        self.stop()

    @discord.ui.button(label="Reject", style=discord.ButtonStyle.red, emoji="🛑")
    async def returnFalse(self, interaction: discord.Interaction, button):
        await interaction.response.send_message("Aborting...", ephemeral=True)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) aborts adding {self.title} ({self.game_id}) to the RGIT Table.")
        self.stop()

async def addGamePrompt(interaction: discord.Interaction, title):
    
    # If the user indicates they want to add a game, run this function.

    try:
        
        itad_search = ItadGameSearchHandler(title)
        logger.debug(f"{interaction.user.name} ({interaction.user.id}) has passed all exception checks for [{title}] at [addGamePrompt()].")
        await interaction.response.defer(ephemeral=True)
        embed = discord.Embed(
            title=itad_search.get_title(),
            color=16777215 
            ) 
        embed.set_image(url=itad_search.get_boxart())
       
        if itad_search.get_release_date() == "Unreleased":
            embed.add_field(name="Released", value="Unreleased", inline=False)
        else:
             embed.add_field(name="Released", value=datetime.datetime.strptime(itad_search.get_release_date(), '%Y-%m-%d').strftime('%B %d, %Y'), inline=False)
       
        embed.add_field(name="Publishers", value=', '.join(itad_search.get_publishers()), inline=False)
        embed.add_field(name="Tags", value=', '.join(itad_search.get_tags()), inline=False)
        embed.set_footer(text="Powered by the IsThereAnyDeal API.")
        view = AddView(game_title=itad_search.get_title(), game_id=itad_search.get_id())
        await interaction.followup.send(content="Is this the game you wish to add?", embed=embed, view=view, ephemeral=True)
        logger.debug(f"API successfully finds {title} ({itad_search.get_id()}). {interaction.user.name} ({interaction.user.id}) prompted to confirm or deny action.")
        await view.wait()
    
    except ValueError:
        await interaction.response.send_message("The game could not be found. Please try again. Please be *very* specific; special characters and capitalization *do* matter.", ephemeral=True)
        logger.error(f"API unable to find [{title}] for {interaction.user.name} ({interaction.user.id}).")
        return
    
    except RuntimeError:
        await interaction.response.send_message("Due to character limits additional games may not be added. Please speak with Sirdog.")
        logger.critical(f"{interaction.user.name} ({interaction.user.id}) attempted to exceed soft-limit of RGIT games. (P2)")
        return

async def removeGame(interaction: discord.Interaction, title):

     # If the user indicates they want to remove a game, run this function.
            
    rgit_game = ItadGameSearchHandler(title)
    rgit_games_db = DBRGITGames()
    await interaction.response.defer(ephemeral=True)

    if rgit_games_db.check_if_exists(rgit_game.get_id()) == False:
        await interaction.followup.send("The game is not in the database.", ephemeral=True)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) attempted to remove {title} when it wasn't in the RGIT table.")
        return
    
    rgit_games_db.remove_game(rgit_game.get_id())
    await interaction.followup.send("Game removed.", ephemeral=True)
    logger.info(f"{interaction.user.name} ({interaction.user.id}) successfully removes {title} ({rgit_game.get_id()}) from the RGIT Table.")


# Typical Discord cog class creation

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
 # Add or remove games from the RGIT games table based on ITAD API data.

    @app_commands.command(name="rgit-edit", description="Add or remove a game from the RGIT table.")
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
 # Get a raw list of every game in the table.

    @app_commands.command(name="rgit-list", description="List all games in the RGIT table.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def rgitlist(self, interaction: discord.Interaction):

        temporary_list = [] # Initiate an empty list

        for game in db.list_games(): # Running the list_games() method of the RGITGames class, append every game name in the RGIT games table to the initiated list.
            temporary_list.append(f"- {game}")
       
        games = "\n".join(temporary_list) #Join every item in the list together, initiating new lines per item.

        embed = discord.Embed(title="Games List", description=games, color=3800852)
        logger.info(f"{interaction.user.name} ({interaction.user.id}) requested a list of all RGIT games in the table.")
        await interaction.response.send_message(content="The following is a raw list of all games in the RGIT table. This is long and empty. There are tentative plans to make this prettier in future releases.", embed=embed, ephemeral=True)


# --- /rgit-deals --
# Get a list of what games in the RGIT database have deals.
# This will only produce at max 25 (enforced by the ItadGameDealsHandler class) due to Discord embed field limits.

    @app_commands.command(name="rgit-deals", description="Get list of deals for games in the RGIT table.")
    @app_commands.check(check_permissions)
    @app_commands.guilds(GUILD_ID)
    async def rgitdeals(self, interaction: discord.Interaction):

        deals = ItadGameDealsHandler(db.get_ids()) # Get deal data from ITAD API by running a method from DBRGITGames that gives a Python list of all game IDs in the DB.
        name_to_id_dict = db.get_ids_and_names() # Get JSON key/value pairs where the key is a game's ITAD UUID and the value is the game's name. 

        embed = discord.Embed(title=":moneybag: Available Deals", 
                              description="The following are deals, in order from largest cut to lowest cut, for the games in the RGIT table. Due to technical limitations only 25 deals are displayable.",
                              color=3800852
                              )

        for deal in deals.get_deals():  

            # Get a game name's for each iterated deal by mapping the ID given by the ITAD API 
            # against the key/value pairs retrieved from the DB.
            # VVVVVVVVVVVVVVVV
            
            id = deal["id"]
            game_name = name_to_id_dict[id] 

            # ^^^^^^^^^^^^^^^

            deals_amount = "${:0.2f}".format(deal["deals"][0]["price"]["amount"])
            full_amount = "${:0.2f}".format(deal["deals"][0]["regular"]["amount"])

            embed.add_field(name=f"{game_name} ({deal["deals"][0]["cut"]}% Off)", value=f"{deals_amount} ({full_amount}) at [{deal["deals"][0]["shop"]["name"]}]({deal["deals"][0]["url"]})")

        embed.set_footer(text="Powered by the IsThereAnyDeal API.")
        logger.info(f"{interaction.user.name} ({interaction.user.id}) requested a list of deals for RGIT games.")
        await interaction.response.send_message(embed=embed)
        
async def setup(bot):
    await bot.add_cog(itad(bot))