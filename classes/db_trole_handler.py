import sqlite3
from dotenv import load_dotenv

load_dotenv()

import logging
import datetime
from datetime import datetime

logger = logging.getLogger("endurabot." + __name__)


class DBTempRole:
    def __init__(self):
        self.connection = sqlite3.connect("endurabot.db")
        self.cursor = self.connection.cursor()
        check_if_table_exists = """CREATE TABLE IF NOT EXISTS temp_roles(temp_roles_id INTEGER PRIMARY KEY AUTOINCREMENT, temp_roles_name TEXT, temp_roles_disc_id TEXT,
        temp_roles_mod_name TEXT, temp_roles_mod_disc_id TEXT, temp_roles_role_id TEXT, temp_roles_timestamp NUMERIC)"""
        self.cursor.execute(check_if_table_exists)
        self.connection.commit()

    def check_status(self, target_id):

        self.cursor.execute("SELECT temp_roles_disc_id FROM temp_roles")
        tuple = self.cursor.fetchall()
        list = [ints[0] for ints in tuple]

        if target_id in list:
            return True
        else:
            return False

    def add_user(self, target_id, target_name, mod_id, mod_name, role_id, timestamp):
        if self.check_status(str(target_id)) == True:
            self.remove_user_by_id(str(target_id))

        self.cursor.execute(
            f"INSERT INTO temp_roles(temp_roles_disc_id, temp_roles_name, temp_roles_mod_disc_id, temp_roles_mod_name, temp_roles_role_id, temp_roles_timestamp) VALUES (?, ?, ?, ?, ?, ?)",
            (target_id, target_name, mod_id, mod_name, role_id, timestamp),
        )
        self.connection.commit()

    def remove_user_by_timestamp(self, timestamp):
        self.cursor.execute(
            f"DELETE FROM temp_roles WHERE temp_roles_timestamp = ?", (timestamp,)
        )
        self.connection.commit()

    def remove_user_by_id(self, target_id):
        self.cursor.execute(
            f"DELETE FROM temp_roles WHERE temp_roles_disc_id = ?", (target_id,)
        )
        self.connection.commit()

    def get_user_id_by_timestamp(self, timestamp):

        self.cursor.execute(f"SELECT temp_roles_disc_id FROM temp_roles WHERE temp_roles_timestamp = ?", (timestamp,))
        result = self.cursor.fetchone()
        return result[0]

    def get_user_name_by_timestamp(self, timestamp):

        self.cursor.execute(f"SELECT temp_roles_name FROM temp_roles WHERE temp_roles_timestamp = ?", (timestamp,))
        result = self.cursor.fetchone()
        return result[0]

    def get_mod(self, target_id):

        if self.check_status(target_id) == False:
            raise ValueError("User does not have a temporary role.")

        self.cursor.execute(f"SELECT temp_roles_mod_disc_id FROM temp_roles WHERE temp_roles_disc_id = ?", (target_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_role(self, target_id):

        if self.check_status(target_id) == False:
            raise ValueError("User does not have a temporary role.")

        self.cursor.execute(f"SELECT temp_roles_role_id FROM temp_roles WHERE temp_roles_disc_id = ?", (target_id,))
        result = self.cursor.fetchone()

        return result[0]

    def get_role_by_timestamp(self, timestamp):

        self.cursor.execute(f"SELECT temp_roles_role_id FROM temp_roles WHERE temp_roles_timestamp = ?", (timestamp,))
        result = self.cursor.fetchone()

        return result[0]

    def check_time(self, target_id):
        if self.check_status(target_id) == False:
            raise ValueError("User does not have a temporary role.")

        self.cursor.execute(f"SELECT temp_roles_timestamp FROM temp_roles WHERE temp_roles_disc_id = ?", (target_id,))
        result = self.cursor.fetchone()

        timestamp_str = result[0]

        dt_object = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S")

        epoch = round(dt_object.timestamp())

        return epoch

    def get_timestamps(self):
        self.cursor.execute("SELECT temp_roles_timestamp FROM temp_roles")
        timestamps = [datetime.strptime(id[0], "%Y-%m-%d %H:%M:%S") for id in self.cursor.execute("SELECT temp_roles_timestamp FROM temp_roles")]
        return timestamps