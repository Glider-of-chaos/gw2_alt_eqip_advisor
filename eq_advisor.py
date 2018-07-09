import json
import configparser
import os
import pdb
import importlib.util
import urllib.request

# TODO: remake next line. it's godawful
current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
#pdb.set_trace()
personal_config = configparser.ConfigParser()
personal_config.read(config_path)
#pdb.set_trace()

gw2item_path = os.path.join(current_dir, 'gw2item.py')
spec = importlib.util.spec_from_file_location("gw2item", gw2item_path)
gw2item = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw2item)

gw2apiwrapper_path = os.path.join(current_dir, 'gw2apiwrapper.py')
spec = importlib.util.spec_from_file_location("gw2apiwrapper", gw2apiwrapper_path)
gw2api = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gw2api)

db_connector_path = os.path.join(current_dir, 'db_connector.py')
spec = importlib.util.spec_from_file_location("db_connector", db_connector_path)
db_connector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(db_connector)

exceptions_path = os.path.join(current_dir, 'exceptions.py')
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path)
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)

CHARACTER = 'character'
CHARACTERS = 'characters'
ITEM = 'item'
BANK = 'bank'

weapon_count_by_prof = {'Thief': {'axe': 0,
                                'dagger': 2,
                                'focus': 0,
                                'greatsword': 0,
                                'hammer': 0,
                                'harpoon_gun': 1,
                                'longbow': 0,
                                'mace': 0,
                                'pistol': 2,
                                'rifle': 1,
                                'scepter': 0,
                                'shield': 0,
                                'short_bow': 1,
                                'spear': 1,
                                'staff': 1,
                                'sword': 1,
                                'torch': 0,
                                'trident': 0,
                                'warhorn': 0},
                        'Revenant': {'axe': 1,
                                'dagger': 0,
                                'focus': 0,
                                'greatsword': 0,
                                'hammer': 1,
                                'harpoon_gun': 0,
                                'longbow': 0,
                                'mace': 1,
                                'pistol': 0,
                                'rifle': 0,
                                'scepter': 0,
                                'shield': 1,
                                'short_bow': 1,
                                'spear': 1,
                                'staff': 1,
                                'sword': 2,
                                'torch': 0,
                                'trident': 1,
                                'warhorn': 0}}

important_slots = ("HelmAquatic",
                    "Backpack",
                    "Coat",
                    "Boots",
                    "Gloves",
                    "Helm",
                    "Leggings",
                    "Shoulders",
                    "Accessory1",
                    "Accessory2",
                    "Ring1",
                    "Ring2",
                    "Amulet",
                    "WeaponAquaticA",
                    "WeaponAquaticB",
                    "WeaponA1",
                    "WeaponA2",
                    "WeaponB2")

def get_char_wear_ids(api_wrapper, char):
    wear_ids = dict()
    inv_json = json.loads(api_wrapper.get_json_string(CHARACTER, char))
    wear_json = inv_json['equipment']

    for item in wear_json:
        if item['slot'] in important_slots:
            wear_ids[item['slot']] = item['id']

    return wear_ids

def get_char_all_items(api_wrapper, char):
    item_ids = list()
    inv_json = json.loads(api_wrapper.get_json_string(CHARACTER, char))
    wear_json = inv_json['equipment']
    for item in wear_json:
        item_ids.append(item['id'])

    bags_json = inv_json['bags']
    for bag in bags_json:
        bag_contents = bag['inventory']
        for item in bag_contents:
            if item != None:
                #pdb.set_trace()
                item_ids.append(item['id'])

    return item_ids

def print_char_equipment_score(api_wrapper, char):
    char_equipment = get_char_wear_ids(api_wrapper, char)
    char_equip_score = 0
    char_max_score = 0
    for equip_slot in char_equipment:
        equip_id = char_equipment[equip_slot]
        equip_json = json.loads(api_wrapper.get_json_string(ITEM, equip_id))
        equip = gw2item.GW2Item(equip_json)

        slot_max_score = 80 * 1.1
        slot_equip_score = equip.show_level() * equip.show_rarity_value()

        char_max_score += slot_max_score
        char_equip_score += slot_equip_score

        if slot_equip_score < slot_max_score:
            print("{0} score = {1}".format(equip_slot, slot_equip_score))
            print("\trarity = {0}".format(equip.show_rarity()))
            print("\tlevel = {0}".format(equip.show_level()))

    print("equipment score is {0} out of {1}".format(char_equip_score, char_max_score))

def get_item_string(db_conn, api_wrapper, item_id):
    try:
        item_str = db_conn.get_item_json(item_id)
        item_json = json.loads(item_str)
        return item_json
    except db_connector.exceptions.NoDBItemError:
        try:
            item_json = api_wrapper.get_json_string(ITEM, item_id)
            db_conn.add_item(item_id, str(item_json))
            return item_json
        except urllib.error.HTTPError as err:
            print('failed to get an item {0}'.format(item_id))
            print(err)
            return None
        except Exception as err:
            print('getting item from api and adding to db failed')
            print(err)
            return None
    except Exception as err:
        print('getiing item from db failed with unknow error')
        print(err)
        return None

def get_inv_data(api_wrapper):
    chars = json.loads(api_wrapper.get_json_string(CHARACTERS))
    char_jsons = dict()
    dbc = db_connector.DBConnector()

    for char in chars:
        char_jsons[char] = json.loads(api_wrapper.get_json_string(CHARACTER, char))
    bank_json = json.loads(api_wrapper.get_json_string(BANK))
    for bank_item in bank_json:
        if bank_item != None:
            item_id = bank_item['id']
            item_json = get_item_string(dbc, api_wrapper, item_id)
    for char in chars:
        char_item_ids = get_char_all_items(api_wrapper, char)
        for item_id in char_item_ids:
            item_json = get_item_string(dbc, api_wrapper, item_id)

def find_runaway_soulbound(api_wrapper):
    runaways = list()
    chars = json.loads(api_wrapper.get_json_string(CHARACTERS))
    #pdb.set_trace()
    char_jsons = dict()
    for char in chars:
        char_jsons[char] = json.loads(api_wrapper.get_json_string(CHARACTER, char))
    # starting with bank
    bank_json = json.loads(api_wrapper.get_json_string(BANK))
    #pdb.set_trace()
    for char in chars:
        print("looking for runaway soulbound items for {0}".format(char))
        for bank_item in bank_json:
            if bank_item != None:
                if 'binding' in bank_item:
                    if bank_item['binding'] == 'Character':
                        if bank_item['bound_to'] == char:
                            runaways.append((char, 'bank', bank_item['id']))
        for other_char in chars:
            if other_char != char:
                other_char_json = char_jsons[other_char]
                other_char_bags = other_char_json['bags']
                for bag in other_char_bags:
                    for other_char_item in bag['inventory']:
                        if other_char_item != None:
                            if 'binding' in other_char_item:
                                if other_char_item['binding'] == 'Character':
                                    if other_char_item['bound_to'] == char:
                                        runaways.append((char, other_char, other_char_item['id']))
    print(runaways)
    print("and now with additional flare")
    pdb.set_trace()
    for runaway in runaways:
        item_json = json.loads(api_wrapper.get_json_string(ITEM, runaway[2]))
        item = gw2item.GW2Item(item_json)
        item_name = item.show_name()
        print ("{0} - his item named {2} ran to - {1}".format(runaway[0], runaway[1], item_name))

def main():
    c1 = personal_config['TOKEN']['char1']
    token = personal_config['TOKEN']['token']
    api_wrapper = gw2api.ApiWrapper(token)
    dbc = db_connector.DBConnector()
    #print_char_equipment_score(api_wrapper, c1)
    #find_runaway_soulbound(api_wrapper)
    #tst_json = dbc.get_item_json_string('3')
    #print(tst_json)
    #print(type(tst_json))
    get_inv_data(api_wrapper)


if __name__ == "__main__":
    main()

