import sqlite3
import discord
from dotenv import load_dotenv

load_dotenv()

import logging

logger = logging.getLogger('endurabot.' + __name__)

class DBRGITGames():
    def __init__(self):
        self.connection = sqlite3.connect('endurabot.db')
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS rgit_games(rgit_games_id INTEGER PRIMARY KEY AUTOINCREMENT, rgit_games_itad_id TEXT,
        rgit_games_title TEXT, rgit_games_added_by TEXT, rgit_games_timestamp NUMERIC)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()

    def check_if_exists(self, id):
        
        self.cursor.execute(f"SELECT 1 FROM rgit_games WHERE rgit_games_itad_id = ?", (id,))
        data = self.cursor.fetchone()

        if data:
            return not None
        else:
            return False

    def add_game(self, title, game_id, user_id):

        if not self.check_if_exists(game_id) == False:
            raise ValueError("Game already in table.")
        
        self.cursor.execute("SELECT COUNT(*) from rgit_games")
        row_count = self.cursor.fetchone()

        if row_count[0] >= 150:
            raise RuntimeError("Maximum games has been hit.")

        timestamp = round(discord.utils.utcnow().timestamp())
        self.cursor.execute(f"INSERT INTO rgit_games (rgit_games_itad_id, rgit_games_title, rgit_games_added_by, rgit_games_timestamp) VALUES (?, ?, ?, ?)", (game_id, title, user_id, timestamp))
        self.connection.commit()

    def remove_game(self, game_id):
        
        if self.check_if_exists(game_id) == False:
            raise ValueError("Game not in the table.")
        
        self.cursor.execute(f"DELETE FROM rgit_games WHERE rgit_games_itad_id = ?", (game_id,))
        self.connection.commit()

    def list_games(self):

        self.cursor.execute("SELECT rgit_games_title FROM rgit_games")
        games = [game[0] for game in self.cursor.execute("SELECT rgit_games_title FROM rgit_games")]
        return sorted(games)
    
    def get_ids(self):

        self.cursor.execute("SELECT rgit_games_itad_id FROM rgit_games")
        ids = [id[0] for id in self.cursor.execute("SELECT rgit_games_itad_id FROM rgit_games")]
        return ids
    
    def get_ids_and_names(self):

        self.cursor.execute("SELECT rgit_games_itad_id, rgit_games_title FROM rgit_games")
        return dict(self.cursor.fetchall())