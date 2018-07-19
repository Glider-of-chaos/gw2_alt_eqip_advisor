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

class ItemSlot:

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

    def __init__(self, slot_string, location, id_string):
        #pdb.set_trace()
        self.flat_dict = {'rarity': 'Junk',
                        'level': 0}
        self.attributes_json = {'AgonyResistance': 0,
                            'BoonDuration': 0,
                            'ConditionDamage': 0,
                            'ConditionDuration': 0,
                            'CritDamage': 0,
                            'Healing': 0,
                            'Power': 0,
                            'Precision': 0,
                            'Toughness': 0,
                            'Vitality': 0}
        if slot_string == None:
            self.flat_dict['empty'] = True
        else:
            self.flat_dict['empty'] = False
            self.location = location
            self.slot_string = slot_string
            self.slot_json = json.loads(slot_string)

            if 'slot' in self.slot_json:
                self.flat_dict['equipped'] = True
            else:
                self.flat_dict['equipped'] = False

            if 'stats' in self.slot_json:
                self.attributes_json = self.slot_json['stats']['attributes']

            if 'binding' in self.slot_json:
                self.flat_dict['binding'] = self.slot_json['binding']
                if 'bound_to' in self.slot_json:
                    self.flat_dict['bound_to'] = self.slot_json['bound_to']
            
        if id_string == 'None':
            self.flat_dict['empty_id'] = True
        else:
            self.id_string = id_string
            self.id_json = json.loads(id_string)
            self.flat_dict['name'] = self.id_json['name']
            if 'type' in self.id_json:
                self.flat_dict['type'] = self.id_json['type']
            if 'level' in self.id_json:
                self.flat_dict['level'] = self.id_json['level']
            if 'rarity' in self.id_json:
                self.flat_dict['rarity'] = self.id_json['rarity']
            if 'icon' in self.id_json:
                self.flat_dict['icon'] = self.id_json['icon']
            if 'details' in self.id_json:
                details_json = self.id_json['details']
                if 'type' in details_json:
                    self.flat_dict['deep_type'] = details_json['type']
                if 'weight_class' in details_json:
                    self.flat_dict['armor_weight'] = details_json['weight_class']
                if 'infix_upgrade' in details_json:
                    att_json = details_json['infix_upgrade']['attributes']
                    for att in att_json:
                        self.attributes_json[att['attribute']] = att['modifier']

    def __repr__(self):
        item_name = ''
        if 'name' in self.flat_dict:
            item_name = f'{self.flat_dict["name"]}'
        else:
            item_name = 'UNNAMED ITEM'

        rep_string = f'{item_name} ({self.flat_dict["rarity"]}, level {self.flat_dict["level"]})'
        return rep_string

    def show_type(self):
        if 'type' in self.flat_dict:
            return self.flat_dict["type"]
        else:
            return None

    def show_deep_type(self):
        return self.flat_dict['deep_type']

    def show_level(self):
        return self.flat_dict["level"]

    def show_rarity(self):
        return self.flat_dict["rarity"]

    def show_name(self):
        return self.flat_dict['name']

    def show_rarity_value(self):
        rarity_str = self.show_rarity()
        #pdb.set_trace()
        #print(rarity_str)
        #print(self.rarity_rating)
        rating = self.rarity_rating[rarity_str]
        return rating

    def show_att_score(self, att_values):
        att_score = 0
        for att in att_values:
            att_score += self.attributes_json[att] * att_values[att]
        return att_score


