import json
import configparser
import os
import pdb
import importlib.util

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

def get_chars(token):
    request_link = "https://api.guildwars2.com/v2/characters?access_token=" + token
    response = urllib.request.urlopen(request_link)

    if response.getcode() == 200:
        chars_str = response.read().decode()
        chars_str = chars_str.replace("\n", "").replace("[", "").replace("]", "").replace('"', "").replace("  ", "")
        chars_arr = chars_str.split(",")
        return chars_arr


def get_char_equipment_ids(char, token):
    api_wrapper = gw2api.ApiWrapper(token)
    wear_ids = dict()
    inv_json = api_wrapper.get_json(CHARACTER, char)
    wear_json = inv_json['equipment']

    for item in wear_json:
        if item['slot'] in important_slots:
            wear_ids[item['slot']] = item['id']

    return wear_ids

def print_char_equipment_score(char, token):
    char_equipment = get_char_equipment_ids(char, token)
    char_eqip_score = 0
    char_max_score = 0
    for eq_slot in char_equipment:
        eqip_id = char_equipment[eq_slot]
        eq = gw2item.GW2Item(eqip_id)

        slot_max_score = 80 * 1.1
        slot_equip_score = eq.show_level() * eq.show_rarity_value()

        char_max_score += slot_max_score
        char_eqip_score += slot_equip_score

        if slot_equip_score < slot_max_score:
            print("{0} score = {1}".format(eq_slot, slot_equip_score))
            print("\trarity = {0}".format(eq.show_rarity()))
            print("\tlevel = {0}".format(eq.show_level()))


    print("eq score is {0} out of {1}".format(char_eqip_score, char_max_score))


def main():
    
    c1 = personal_config['TOKEN']['char1']
    token = personal_config['TOKEN']['token']
    print_char_equipment_score(c1, token)

if __name__ == "__main__":
    main()
