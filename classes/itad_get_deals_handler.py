import os
from dotenv import load_dotenv
from itertools import islice
from utils.config_loader import SETTINGS_DATA

load_dotenv()

import requests
import logging

logger = logging.getLogger('endurabot.' + __name__)
API_TOKEN = os.getenv('itad-token')

class ItadGameDealsHandler():
    def __init__(self, deals_list):

        deals_url = "https://api.isthereanydeal.com/games/prices/v3"
        deals_header = {'key': API_TOKEN}

        response = requests.post(deals_url, params=deals_header, json=deals_list)

        if self.check_connection() == False:
            raise TypeError("API token missing or invalid.")

        if response.status_code == 200:
            deals = response.json()
        else:
            raise ValueError("Invalid input.")

        self.deals = deals
        self.list_of_ids = deals_list

    def check_connection(self):
        url = "https://api.isthereanydeal.com/games/prices/v3"
        deals_header = {'key': API_TOKEN}

        response = requests.post(url, params=deals_header, json=["01945ff9-a71b-72ca-a4a9-c245c58bb561"])
        data = response.json()

        try:
            data["status_code"]
            logger.debug(f"A tested API connection failed.")
            return False
        except TypeError:
            return True

    def get_deals(self):
        deals_sorted = sorted(self.deals, key=lambda x: x['deals'][0]['price']['amount'])

        blacklisted_ids = list(SETTINGS_DATA["blacklisted_itad_shops"].values())

        for game in deals_sorted:
            valid_offers = [
                    offer for offer in game['deals'] 
                    if offer['shop']['id'] not in blacklisted_ids
                ]
        
            game['deals'] = valid_offers

        deals_cut = list(islice(deals_sorted, 25))
        return deals_cut