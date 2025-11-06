import sqlite3
from dotenv import load_dotenv

load_dotenv()

import logging
import datetime
from datetime import datetime

logger = logging.getLogger("endurabot." + __name__)


class DBTakeL:
    def __init__(self):
        self.connection = sqlite3.connect("endurabot.db")
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS users_with_l(users_with_l_id INTEGER PRIMARY KEY AUTOINCREMENT, users_with_l_name TEXT, users_with_l_disc_id NUMERIC,
        users_with_l_mod_name TEXT, users_with_l_mod_disc_id NUMERIC, users_with_l_timestamp NUMERIC)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()

    def check_status(self, target_id):

        self.cursor.execute("SELECT users_with_l_disc_id FROM users_with_l")
        tuple = self.cursor.fetchall()
        list = [ints[0] for ints in tuple]

        if target_id in list:
            return True
        else:
            return False

    def add_user(self, target_id, target_name, mod_id, mod_name, timestamp):
        if self.check_status(target_id) == True:
            self.remove_user_by_id(target_id)

        self.cursor.execute(
            f"INSERT INTO users_with_l(users_with_l_disc_id, users_with_l_name, users_with_l_mod_disc_id, users_with_l_mod_name, users_with_l_timestamp) VALUES (?, ?, ?, ?, ?)",
            (target_id, target_name, mod_id, mod_name, timestamp),
        )
        self.connection.commit()

    def remove_user_by_timestamp(self, timestamp):
        self.cursor.execute(
            f"DELETE FROM users_with_l WHERE users_with_l_timestamp = ?", (timestamp,)
        )
        self.connection.commit()

    def remove_user_by_id(self, target_id):
        self.cursor.execute(
            f"DELETE FROM users_with_l WHERE users_with_l_disc_id = ?", (target_id,)
        )
        self.connection.commit()

    def get_user_id_by_timestamp(self, timestamp):

        self.cursor.execute(f"SELECT users_with_l_disc_id FROM users_with_l WHERE users_with_l_timestamp = ?", (timestamp,))
        result = self.cursor.fetchone()
        return result[0]

    def get_user_name_by_timestamp(self, timestamp):

        self.cursor.execute(f"SELECT users_with_l_name FROM users_with_l WHERE users_with_l_timestamp = ?", (timestamp,))
        result = self.cursor.fetchone()
        return result[0]

    def get_mod(self, target_id):
        if self.check_status(target_id) == False:
            raise ValueError("User does not have the L.")

        self.cursor.execute(f"SELECT users_with_l_mod_disc_id FROM users_with_l WHERE users_with_l_disc_id = ?", (target_id,))
        result = self.cursor.fetchone()

        return result[0]

    def check_time(self, target_id):
        if self.check_status(target_id) == False:
            raise ValueError("User does not have the L.")

        self.cursor.execute(f"SELECT users_with_l_timestamp FROM users_with_l WHERE users_with_l_disc_id = ?", (target_id,))
        result = self.cursor.fetchone()

        timestamp_str = result[0]

        dt_object = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        epoch = round(dt_object.timestamp())

        return epoch

    def get_timestamps(self):
        self.cursor.execute("SELECT users_with_l_timestamp FROM users_with_l")
        timestamps = [datetime.strptime(id[0], "%Y-%m-%d %H:%M:%S") for id in self.cursor.execute("SELECT users_with_l_timestamp FROM users_with_l")]
        return timestamps

#db = DBTakeL()
#print(db.get_user_by_timestamp("2025-11-05 21:22:05.642560"))
