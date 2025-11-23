import sqlite3
from dotenv import load_dotenv

load_dotenv()

import logging
from utils.config_loader import SETTINGS_DATA

logger = logging.getLogger("endurabot." + __name__)

class RquoteUsed:
    def __init__(self):
        self.connection = sqlite3.connect("endurabot.db")
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS rquote_used(rquote_used_id INTEGER PRIMARY KEY AUTOINCREMENT, rquote_used_msg_id TEXT)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()

    def check_status(self, msg_id):
        self.cursor.execute("SELECT rquote_used_msg_id FROM rquote_used")
        tuple = self.cursor.fetchall()
        list = [ints[0] for ints in tuple]

        if msg_id in list:
            return True
        else:
            return False
        
    def get_row_count(self):
        self.cursor.execute("SELECT Count(*) FROM rquote_used")
        count = self.cursor.fetchone()
        return count[0]
    
    def delete_oldest_row(self):
        self.cursor.execute("DELETE FROM rquote_used WHERE rowid=(SELECT MIN(rquote_used_id) FROM rquote_used)")
        self.connection.commit()

    def add_msg(self, msg_id):
        if self.check_status(msg_id) == True:
            raise ValueError("Message already in table.")
        
        if self.get_row_count() >= SETTINGS_DATA["max_old_quotes"]:
            self.delete_oldest_row()

        self.cursor.execute(f"INSERT INTO rquote_used(rquote_used_msg_id) VALUES (?)", (msg_id,))
        self.connection.commit()