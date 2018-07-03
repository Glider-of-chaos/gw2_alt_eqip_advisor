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

# TODO: substitute this with get_json?
def get_chars():
    base_api_url = "https://api.guildwars2.com/v2"
    token = personal_config['TOKEN']['token']
    request_link = "{0}/{1}?access_token={2}".format(base_api_url, CHARACTERS, token)
    response = urllib.request.urlopen(request_link)

    if response.getcode() == 200:
        chars_str = response.read().decode()
        chars_str = chars_str.replace("\n", "").replace("[", "").replace("]", "").replace('"', "").replace("  ", "")
        chars_arr = chars_str.split(",")
        return chars_arr


def get_char_wear_ids(api_wrapper, char):
    wear_ids = dict()
    inv_json = api_wrapper.get_json(CHARACTER, char)
    wear_json = inv_json['equipment']

    for item in wear_json:
        if item['slot'] in important_slots:
            wear_ids[item['slot']] = item['id']

    return wear_ids

def get_char_all_items(api_wrapper, char):
    item_ids = list()
    inv_json = api_wrapper.get_json(CHARACTER, char)
    wear_json = inv_json['equipment']
    for item in wear_json:
        item_ids.append(item['id'])

    bags_json = inv_json['bags']
    for bag in bags_json:
        for item in bag:
            item_ids.append(item['id'])

    return item_ids

def print_char_equipment_score(api_wrapper, char):
    char_equipment = get_char_wear_ids(api_wrapper, char)
    char_equip_score = 0
    char_max_score = 0
    for equip_slot in char_equipment:
        equip_id = char_equipment[equip_slot]
        equip_json = api_wrapper.get_json(ITEM, equip_id)
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

def find_runaway_soulbound(api_wrapper, char):
    runaways = list()
    print("looking for runaway soulbound items for {0}".format(char))
    chars = get_chars()
    # starting with bank
    bank_json = api_wrapper.get_json(BANK)
    
    pdb.set_trace()
    for bank_item in bank_json:
        #print('=======================')
        #print(bank_item)
        #print(type(bank_item))
        #bank_item = bank_json[bank_item_key]
        if bank_item != None:
            if 'binding' in bank_item:
                if bank_item['binding'] == 'Character':
                    if bank_item['bound_to'] == char:
                        runaways.append(('bank', bank_item['id']))
    for other_char in chars:
        if other_char != char:
            other_char_json = api_wrapper.get_json(CHARACTER, other_char)
            other_char_bags = other_char_json['bags']
            for bag in other_char_bags:
                for other_char_item in bag['inventory']:
                    if other_char_item != None:
                        if 'binding' in other_char_item:
                            if other_char_item['binding'] == 'Character':
                                if other_char_item['bound_to'] == char:
                                    runaways.append((other_char, other_char_item['id']))
    print(runaways)
    print("and now with additional flare")
    for runaway in runaways:
        item = gw2item.GW2Item(runaway[1])
        item_name = item['name']
        print ("{0} - holds - {1}".format(runaway[0], item_name))





def main():
    c1 = personal_config['TOKEN']['char1']
    token = personal_config['TOKEN']['token']
    api_wrapper = gw2api.ApiWrapper(token)
    #print_char_equipment_score(api_wrapper, c1)
    find_runaway_soulbound(api_wrapper, c1)


if __name__ == "__main__":
    main()

