import logging
import sys
import datetime

# Custom logging levels
UNAUTHORIZED = 35
logging.addLevelName(UNAUTHORIZED, 'UNAUTHORIZED')

COOLDOWN = 25
logging.addLevelName(COOLDOWN, 'COOLDOWN')

BOOT = 26
logging.addLevelName(BOOT, 'BOOT')

INVITES = 39
logging.addLevelName(INVITES, 'INVITES')

# Custom filter so that debug messages go to their own file.
class DebugOnlyFilter(logging.Filter):
    def filter(self, record):
        return record.levelno == logging.DEBUG


# Custom formatting for BOOT
class CustomBootFormatter(logging.Formatter):
    def __init__(self, fmt=None, datefmt=None, style='%'):
        super().__init__(fmt, datefmt, style)
        self.default_formatter = logging.Formatter(fmt, datefmt, style)
        self.boot_formatter = logging.Formatter('%(message)s', datefmt=None, style=style)

    def format(self, record):
        if record.levelno == BOOT:
            return self.boot_formatter.format(record)
        else:
            return self.default_formatter.format(record)

# Rest of logging configuration as a function that can be called in main.py
def configure_logging():
    logger = logging.getLogger('endurabot')
    logger.setLevel(logging.DEBUG)

    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO) 

    standard_formatter = CustomBootFormatter( 
        fmt='[%(asctime)s]:%(levelname)s:%(name)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    ) 

    file_handler = logging.FileHandler(filename="logs/endurabot.log", encoding='utf-8', mode='a')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(standard_formatter)
    logger.addHandler(file_handler)
    discord_logger.addHandler(file_handler)   


    file_handler_debug = logging.FileHandler(filename="logs/endurabot_debug.log", encoding='utf-8', mode='a')
    file_handler_debug.setLevel(logging.DEBUG)
    file_handler_debug.setFormatter(standard_formatter)
    file_handler_debug.addFilter(DebugOnlyFilter()) # Apply the debug-only filter
    logger.addHandler(file_handler_debug)
    discord_logger.addHandler(file_handler_debug)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(standard_formatter)
    logger.addHandler(console_handler)
    discord_logger.addHandler(console_handler)
    
    now = datetime.datetime.now()
    boot_message = f"--- {now.strftime('%A, %B %d, %Y (%Y%m%d)')} | {now.strftime('%H:%M')} ---"
    logger.log(BOOT, boot_message)

    return logger