import urllib.request
import json

important_slota = ("HelmAquatic",
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
    request_link = "https://api.guildwars2.com/v2/characters/" + char + "?access_token=" + token
    response = urllib.request.urlopen(request_link)
    wear_ids = dict()

    if response.getcode() == 200:
        inv_str = response.read().decode()
        inv_json = json.loads(inv_str)
        wear_json = inv_json['equipment']

        for item in wear_json:
            if item['slot'] in important_slota:
                wear_ids[item['slot']] = item['id']

    return wear_ids
