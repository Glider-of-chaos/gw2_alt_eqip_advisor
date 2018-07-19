import json
import configparser
import os
import pdb
import importlib.util
import urllib.request

# TODO: remake next line. it's godawful
current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
personal_config = configparser.ConfigParser()
personal_config.read(config_path)
weapon_count_path = os.path.join(current_dir, 'weapon_count.ini')
weapon_count_config = configparser.ConfigParser()
weapon_count_config.optionxform = str
weapon_count_config.read(weapon_count_path)

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

relevant_types = ('Armor',
                'Weapon',
                'Trinket',
                'Back')

armor_count = {'HelmAquatic': 1,
            'Backpack': 1,
            'Coat': 1,
            'Boots': 1,
            'Gloves': 1,
            'Helm': 1,
            'Leggings': 1,
            'Shoulders': 1,
            'Accessory': 2,
            'Ring': 2,
            'Amulet': 1}

profession_armor = {'Guardian': 'Heavy',
                'Revenant': 'Heavy',
                'Warrior': 'Heavy',
                'Engineer': 'Medium',
                'Ranger': 'Medium',
                'Thief': 'Medium',
                'Elementalist': 'Light',
                'Mesmer': 'Light',
                'Necromancer': 'Light'}

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

def char_filled_slots(char_string):
    filled_slots = list()
    inv_json = json.loads(char_string)
    all_slots = inv_json['equipment']

    for bag in inv_json['bags']:
        all_slots.extend(bag['inventory'])

    for slot in all_slots:
        if slot != None:
            filled_slots.append(slot)

    return filled_slots


def print_char_equipment_score(api_wrapper, char):
    char_equipment = get_char_wear_ids(api_wrapper, char)
    char_equip_score = 0
    char_max_score = 0
    for equip_slot in char_equipment:
        equip_id = char_equipment[equip_slot]
        equip_str = api_wrapper.get_json_string(ITEM, equip_id)
        equip = gw2item.ItemSlot(None, char, equip_str)

        slot_max_score = 80 * 1.1
        slot_equip_score = equip.show_level() * equip.show_rarity_value()

        char_max_score += slot_max_score
        char_equip_score += slot_equip_score

        if slot_equip_score < slot_max_score:
            print("{0} score = {1}".format(equip_slot, slot_equip_score))
            print("\trarity = {0}".format(equip.show_rarity()))
            print("\tlevel = {0}".format(equip.show_level()))

    print("equipment score is {0} out of {1}".format(char_equip_score, char_max_score))

def print_char_att_score(api_wrapper, char):
    char_equipment = get_char_wear_ids(api_wrapper, char)
    char_att_score = 0
    for equip_slot in char_equipment:
        equip_id = char_equipment[equip_slot]
        equip_str = api_wrapper.get_json_string(ITEM, equip_id)
        equip = gw2item.ItemSlot(None, char, equip_str)

        att_values = { 'Power': 1.4,
                'Precision': 1,
                'CritDamage':1}

        slot_att_score = equip.show_att_score(att_values)

        char_att_score += slot_att_score

        print("{0} score = {1}".format(equip_slot, slot_att_score))
        print("\trarity = {0}".format(equip.show_rarity()))
        print("\tlevel = {0}".format(equip.show_level()))

    print("full equipment score is {0}".format(char_att_score))

def get_item_string(db_conn, api_wrapper, item_type, item_id):
    try:
        item_str = db_conn.get_item_json(item_type, item_id)
        #item_json = json.loads(item_str)
        #return item_json
        return item_str
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
            item_json = get_item_string(dbc, api_wrapper, ITEM, item_id)
    for char in chars:
        char_item_ids = get_char_all_items(api_wrapper, char)
        for item_id in char_item_ids:
            item_json = get_item_string(dbc, api_wrapper, ITEM, item_id)

def get_char_donations(api_wrapper, char_string, char_values):
    dbc = db_connector.DBConnector()
    filled_slots = char_filled_slots(char_string)
    char_json = json.loads(char_string)
    prof = char_json['profession']
    armor_weight = profession_armor[prof]
    personal_weapon_list = weapon_count_config[prof]

    donations = list()
    personal_gear_types = dict()
    personal_gear_scores = dict()
    personal_gear_items = dict()

    for armor in armor_count:
        for i in range(armor_count[armor]):
            slot_name = f'{armor}_{armor_count[armor]}'
            personal_gear_types[slot_name] = armor
            personal_gear_scores[slot_name] = 0

    for weapon in personal_weapon_list:
        #print(weapon)
        #print(personal_weapon_list[weapon])
        for i in range(int(personal_weapon_list[weapon])):
            slot_name = f'{weapon}_{personal_weapon_list[weapon]}'
            personal_gear_types[slot_name] = weapon
            personal_gear_scores[slot_name] = 0

    for filled_slot in filled_slots:
        for_donation = True
        id_string = get_item_string(dbc, api_wrapper, ITEM, filled_slot['id'])
        #pdb.set_trace()
        slot_item = gw2item.ItemSlot(json.dumps(filled_slot), char_json['name'], id_string)
        if slot_item.show_type() in relevant_types:
            #pdb.set_trace()
            for personal_gear_type in personal_gear_types:
                if slot_item.show_deep_type() == personal_gear_types[personal_gear_type]:
                    slot_score = slot_item.show_att_score(char_values)
                    if slot_score > personal_gear_scores[personal_gear_type]:
                        personal_gear_scores[personal_gear_type] = slot_score
                        if personal_gear_type in personal_gear_items:
                            donations.append(personal_gear_items[personal_gear_type])
                        personal_gear_items[personal_gear_type] = slot_item
                        for_donation = False
                        break
        if for_donation:
            donations.append(filled_slot)


    print('char equip:')
    print(personal_gear_items)
    print('donations:')
    print(donations)




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
        item = gw2item.ItemSlot(item_json)
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
    #get_inv_data(api_wrapper)
    #chars = json.loads(api_wrapper.get_json_string(CHARACTERS))
    #for char in chars:
        #print('Equipment for {0}'.format(char))
        #print_char_equipment_score(api_wrapper, char)
    #print_char_att_score(api_wrapper, 'Jink Shadowloom')
    #j_shadowloom_str = api_wrapper.get_json_string(CHARACTER, 'Jink Shadowloom')
    j_shadowloom_str = get_item_string(dbc, api_wrapper, CHARACTER, 'Jink Shadowloom')
    #print('=============')
    #print(j_shadowloom_str)
    #print('=============')
    jink_values =  { 'Power': 1.4,
                'Precision': 1,
                'CritDamage':1}
    get_char_donations(api_wrapper, j_shadowloom_str, jink_values)
    

if __name__ == "__main__":
    main()

