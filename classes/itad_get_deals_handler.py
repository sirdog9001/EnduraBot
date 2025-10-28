import os
from dotenv import load_dotenv
from itertools import islice

load_dotenv()

import requests
import logging

API_TOKEN = os.getenv('itad-token')

class ItadGameDealsHandler():
    def __init__(self, deals_list):
        
        deals_url = "https://api.isthereanydeal.com/games/prices/v3"
        deals_header = {'key': API_TOKEN, 'deals': True, 'capacity': 1}

        response = requests.post(deals_url, params=deals_header, json=deals_list)
        
        if response.status_code == 200:
            deals = response.json()
        else:
            raise ValueError("Invalid input.")

        self.deals = deals
        self.list_of_ids = deals_list

    def get_deals(self):

        deals_sorted = sorted(self.deals, key=lambda x: x['deals'][0]['cut'], reverse=True)
        
        deals_cut = list(islice(deals_sorted, 25))
        return deals_cut