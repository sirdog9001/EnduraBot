import sqlite3
import discord
from dotenv import load_dotenv

load_dotenv()

import logging

logger = logging.getLogger('endurabot.' + __name__)

class DBMonitor():
    def __init__(self):
        self.connection = sqlite3.connect('endurabot.db')
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS member_monitor(member_monitor_id INTEGER PRIMARY KEY AUTOINCREMENT, member_monitor_name TEXT,
        member_monitor_disc_id TEXT, member_monitor_steam_id TEXT, member_monitor_mod_name TEXT, member_monitor_mod_disc_id TEXT,
        member_monitor_reason TEXT, member_monitor_timestamp NUMERIC, member_monitor_level TEXT)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()

    def check_status(self, target_id):

        self.cursor.execute("SELECT member_monitor_disc_id FROM member_monitor")
        tuple = self.cursor.fetchall()
        list = [ints[0] for ints in tuple]

        if target_id in list:
            return True
        else:
            return False

    def add_user(self, target_name, target_disc_id, target_steam_id, mod_name, mod_disc_id, reason, level):
        if self.check_status(target_disc_id) == True:
            raise ValueError("User already being monitored.")

        timestamp = round(discord.utils.utcnow().timestamp())
        self.cursor.execute(f"INSERT INTO member_monitor(member_monitor_name, member_monitor_disc_id, member_monitor_steam_id, member_monitor_mod_name, member_monitor_mod_disc_id, member_monitor_reason, member_monitor_timestamp, member_monitor_level) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (target_name, target_disc_id, target_steam_id, mod_name, mod_disc_id, reason, timestamp, level))
        self.connection.commit()

    def remove_user(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User already not being monitored.")

        self.cursor.execute(f"DELETE FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        self.connection.commit()

    def get_name(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_name FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_steamid(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_steam_id FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_mod_name(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_mod_name FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_mod_id(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_mod_disc_id FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_reason(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_reason FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_timestamp(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_timestamp FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_level(self, target_disc_id):
        if self.check_status(target_disc_id) == False:
            raise ValueError("User not found.")

        self.cursor.execute(f"SELECT member_monitor_level FROM member_monitor WHERE member_monitor_disc_id = ?", (target_disc_id,))
        result = self.cursor.fetchone()

        return result[0]
