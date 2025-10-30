import os
from dotenv import load_dotenv
from itertools import islice

load_dotenv()

import requests
import logging

logger = logging.getLogger('endurabot.' + __name__)
API_TOKEN = os.getenv('itad-token')

class ItadGameDealsHandler():
    def __init__(self, deals_list):

        deals_url = "https://api.isthereanydeal.com/games/prices/v3"
        deals_header = {'key': API_TOKEN, 'deals': True, 'capacity': 1}

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

    def get_deals_by_cut(self):
        deals_sorted = sorted(self.deals, key=lambda x: x['deals'][0]['cut'], reverse=True)

        deals_cut = list(islice(deals_sorted, 25))
        return deals_cut

    def get_deals_by_price(self):
        deals_sorted = sorted(self.deals, key=lambda x: x['deals'][0]['price']['amount'])

        deals_cut = list(islice(deals_sorted, 25))
        return deals_cut

test = ItadGameDealsHandler(["01945ff9-a71b-72ca-a4a9-c245c58bb561"])
print(test.check_connection())