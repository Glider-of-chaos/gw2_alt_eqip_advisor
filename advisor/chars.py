import functools
import json
import re

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flask import Flask

from .db_connector import get_db
from .db_connector import exceptions
from .db_connector import DBConnector

from .gw2apiwrapper import ApiWrapper
from .gw2item import ItemSlot

char_blueprint = Blueprint('chars', __name__, url_prefix = '/char')

attributes = ('BoonDuration',
            'ConditionDamage',
            'ConditionDuration',
            'CritDamage',
            'Healing',
            'Power',
            'Precision',
            'Toughness',
            'Vitality')

@char_blueprint.route('/list', methods = ('GET', 'POST'))
def char_list():
    g.attributes = ('BoonDuration',
            'ConditionDamage',
            'ConditionDuration',
            'CritDamage',
            'Healing',
            'Power',
            'Precision',
            'Toughness',
            'Vitality')

    db = get_db()
    error = None

    chars = db.execute(f"SELECT character.id FROM character LEFT JOIN api_key\
            ON character.api_id=api_key.id\
            WHERE api_key.key_value = '{g.api_key}'").fetchall()

    g.char_names = [char[0] for char in chars]
    
    try:
        print('=== exisiting prefs check ===')
        session['char_att_prefs']
        for char_name in g.char_names:
            session['char_att_prefs'][char_name]
        print('=== exisiting prefs pass ===')
        print('===exisiting char logs ===')
        for char in session['char_att_prefs']:
            print(f'>>>{char}')
            for char_att in session['char_att_prefs'][char]:
                print(f'\t{char_att}: {session["char_att_prefs"][char][char_att]}')
        print('===exisiting char logs ===')
    except (AttributeError, KeyError, NameError):
        print('=== exisiting prefs fail ===')
        char_att_prefs = dict()
        for char_name in g.char_names:
            char_att_prefs[char_name] = dict()
            print('=== why are we here again ===')
            char_att_prefs[char_name]['primary'] = ''
            char_att_prefs[char_name]['secondary1'] = ''
            char_att_prefs[char_name]['secondary2'] = ''
        session['char_att_prefs'] = char_att_prefs

    print('===char prefs - beginning ===')
    for char in session['char_att_prefs']:
        print(f'>>>{char}')
        for char_att in session['char_att_prefs'][char]:
            print(f'\t{char_att}: {session["char_att_prefs"][char][char_att]}')
    print('===char prefs - beginning ===')

    if request.method == 'GET':
        pass
        #return render_template('characters.html', char_names = g.char_names, attributes = g.attributes)
    elif request.method == 'POST':
        #for char in 
        #primary_att = request.form['primary_att_name']
        
        first_form_name = list(request.form.keys())[0]
        char_name = re.search('([^_]+)_', first_form_name).group(1)
        char_att_prefs = session['char_att_prefs']

        char_att_prefs[char_name]['primary'] = request.form[f'{char_name}_primary_att_name']
        char_att_prefs[char_name]['secondary1'] = request.form[f'{char_name}_secondary1_att_name']
        char_att_prefs[char_name]['secondary2'] = request.form[f'{char_name}_secondary2_att_name']

        session['char_att_prefs'] = char_att_prefs

        print('===')
        for char in session['char_att_prefs']:
            print(f'>>>{char}')
            for char_att in session['char_att_prefs'][char]:
                print(f'\t{char_att}: {session["char_att_prefs"][char][char_att]}')
        print('===')
        return redirect(url_for('chars.char_list'))
        
    return render_template('characters.html', char_names = g.char_names, attributes = g.attributes, char_prefs = session['char_att_prefs'])



@char_blueprint.route('/<char_name>', methods = ('GET', ))
def char(char_name):
    if request.method == 'GET':
        db = get_db()
        error = None

        char_row = db.execute(f"SELECT json_string, last_update FROM `character` WHERE id = '{char_name}'").fetchone()
        char_json = char_row[0]
        creation_time = char_row[1]

        if char_json is None:
            error = 'Character not found'

        print('===char prefs in char===')
        for char in session['char_att_prefs']:
            print(f'>>>{char}')
            for char_att in session['char_att_prefs'][char]:
                print(f'\t{char_att}: {session["char_att_prefs"][char][char_att]}')
        print('===char prefs in char===')

        char_values = { session['char_att_prefs'][char_name]['primary']: 1.4,
                session['char_att_prefs'][char_name]['secondary1']: 1,
                session['char_att_prefs'][char_name]['secondary1']:1}
        char_personal_equip = get_char_personal_gear_items(char_json, char_values)

        flash(error)
        return render_template('char.html', content = char_json, timestamp = creation_time, char_personal_equip = char_personal_equip)


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

def get_item_string(db_conn, item_type, item_id):
    try:
        item_str = db_conn.get_item_json(item_type, item_id)
        #item_json = json.loads(item_str)
        #return item_json
        return item_str
    except exceptions.NoDBItemError:
        try:
            #item_json = api_wrapper.get_json_string(ITEM, item_id)
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

def get_char_personal_gear_items(char_string, char_values):


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


    dbc = get_db()
    #db_connector.DBConnector()
    filled_slots = char_filled_slots(char_string)
    char_json = json.loads(char_string)
    prof = char_json['profession']
    armor_weight = profession_armor[prof]
    #personal_weapon_list = weapon_count_config[prof]

    personal_weapon_list = {'Axe': 0,
            'Dagger': 2,
            'focus': 0,
            'Greatsword': 0,
            'Hammer': 0,
            'HarpoonGun': 1,
            'Longbow': 0,
            'Mace': 0,
            'Pistol': 2,
            'Rifle': 1,
            'Scepter': 0,
            'Shield': 0,
            'ShortBow': 1,
            'Spear': 1,
            'Staff': 1,
            'Sword': 1,
            'Torch': 0,
            'Trident': 0,
            'Warhorn': 0}

    donations = list()
    personal_gear_types = dict()
    personal_gear_scores = dict()
    personal_gear_items = dict()

    for armor in armor_count:
        for i in range(armor_count[armor]):
            slot_name = f'{armor}_{i+1}'
            personal_gear_types[slot_name] = armor
            personal_gear_scores[slot_name] = 0

    for weapon in personal_weapon_list:
        #print(weapon)
        #print(personal_weapon_list[weapon])
        for i in range(int(personal_weapon_list[weapon])):
            slot_name = f'{weapon}_{i+1}'
            personal_gear_types[slot_name] = weapon
            personal_gear_scores[slot_name] = 0

    for filled_slot in filled_slots:
        for_donation = True
        local_dbc = DBConnector()
        id_string = get_item_string(local_dbc, 'item', filled_slot['id'])
        #pdb.set_trace()
        slot_item = ItemSlot(json.dumps(filled_slot), char_json['name'], id_string)
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

    return personal_gear_items
