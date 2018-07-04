import urllib.request
import json
import importlib.util
import pdb
import os
import configparser

# TODO: remake next line. it's godawful
current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
personal_config = configparser.ConfigParser()
personal_config.read(config_path)

exceptions_path = os.path.join(current_dir, 'exceptions.py')
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path)
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)

class GW2Item:

    rarity_rating = {
            "Junk" : 0,
            "Basic" : 0.2,
            "Fine" : 0.4,
            "Masterwork" : 0.6,
            "Rare" : 0.8,
            "Exotic" : 1,
            "Ascended" : 1.1,
            "Legendary" : 1.1
            }
    item_string = ""

    def __init__(self, item_json):
        #pdb.set_trace()
        if 'text' in item_json and item_json['text'] == 'no such id':
            raise exceptions.NoSuchItemError()
        else:
            self.item_json = item_json

    def show_type(self):
        return self.item_json["type"]

    def show_level(self):
        return int(self.item_json["level"])

    def show_rarity(self):
        return self.item_json["rarity"]

    def show_name(self):
        return self.item_json['name']

    def show_rarity_value(self):
        rarity_str = self.show_rarity()
        #pdb.set_trace()
        #print(rarity_str)
        #print(self.rarity_rating)
        rating = self.rarity_rating[rarity_str]
        return rating

