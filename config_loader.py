import json
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

VARIABLES_FILE = 'data/variables.json'
MISC_FILE = 'data/misc_text.json'
PERMS_FILE = 'data/permissions.json'

SETTINGS_DATA = {}
MISC_DATA = {}
PERMS_DATA = {}


def load_configs():
    global SETTINGS_DATA

    try:
        with open(VARIABLES_FILE, 'r', encoding='utf-8') as file_object:
            SETTINGS_DATA.clear()
            SETTINGS_DATA.update(json.load(file_object))
            return True

    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical(f"[FATAL ERROR: Cannot load {VARIABLES_FILE}.")
        return False

def load_misc():
    global MISC_DATA

    try:
        with open(MISC_FILE, 'r', encoding='utf-8') as file_object:
            MISC_DATA.clear()
            MISC_DATA.update(json.load(file_object))
            return True

    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical(f"[FATAL ERROR: Cannot load {MISC_FILE}.")
        return False
    
def load_perms():
    global PERMS_DATA

    try:
        with open(PERMS_FILE, 'r', encoding='utf-8') as file_object:
            PERMS_DATA.clear()
            PERMS_DATA.update(json.load(file_object))
            return True

    except (FileNotFoundError, json.JSONDecodeError):
        logger.critical(f"[FATAL ERROR: Cannot load {PERMS_FILE}.")
        return False
    
load_configs()
load_misc()
load_perms()