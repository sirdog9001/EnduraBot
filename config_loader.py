import json
import logging

logger = logging.getLogger('discord')
logger.setLevel(logging.INFO)

VARIABLES_FILE = 'data/variables.json'
MISC_FILE = 'data/misc_text.json'

try:
    with open(VARIABLES_FILE, 'r', encoding='utf-8') as file_object:
        SETTINGS_DATA = json.load(file_object)

except FileNotFoundError:
    logger.critical(f"[FATAL ERROR: {VARIABLES_FILE} not found.")

try:
    with open(MISC_FILE, 'r', encoding='utf-8') as file_object:
        MISC_DATA = json.load(file_object)

except FileNotFoundError:
    logger.critical(f"FATAL ERROR: {MISC_FILE} not found.")