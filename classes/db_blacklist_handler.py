import sqlite3
import discord
from dotenv import load_dotenv

load_dotenv()

import logging

logger = logging.getLogger('endurabot.' + __name__)

class DBBlacklist():
    def __init__(self):
        self.connection = sqlite3.connect('endurabot.db')
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS blacklisted_users(blacklist_id INTEGER PRIMARY KEY AUTOINCREMENT, blacklist_user_id NUMERIC,
        blacklist_mod_id NUMERIC, blacklist_timestamp NUMERIC)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()
    
    def check_status(self, target_id):

        self.cursor.execute("SELECT blacklist_user_id FROM blacklisted_users")
        tuple = self.cursor.fetchall()
        list = [ints[0] for ints in tuple]

        if target_id in list:
            return True
        else:
            return False
    
    def add_user(self, target_id, mod_id):
        if self.check_status(target_id) == True:
            raise ValueError("User already blacklisted.")
        
        timestamp = round(discord.utils.utcnow().timestamp())
        self.cursor.execute(f"INSERT INTO blacklisted_users(blacklist_user_id, blacklist_mod_id, blacklist_timestamp) VALUES (?, ?, ?)", (target_id, mod_id, timestamp))
        self.connection.commit()

    def remove_user(self, target_id):
    
        if self.check_status(target_id) == False:
            raise ValueError("User already not blacklisted.")
        
        self.cursor.execute(f"DELETE FROM blacklisted_users WHERE blacklist_user_id = ?", (target_id,))
        self.connection.commit()