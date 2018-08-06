import functools
import json

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flask import Flask

from .db_connector import get_db

from .gw2apiwrapper import ApiWrapper

char_blueprint = Blueprint('chars', __name__, url_prefix = '/char')


@char_blueprint.route('/list', methods = ('GET', ))
def char_list():
    if request.method == 'GET':
        db = get_db()
        error = None
        #api_wrapper = ApiWrapper(g.api_key)
        #chars_json = api_wrapper.get_json_string('characters', None)

        chars = db.execute(f"SELECT character.id FROM character LEFT JOIN api_key\
                ON character.api_id=api_key.id\
                WHERE api_key.key_value = '{g.api_key}'").fetchall()

        char_names = [char[0] for char in chars]

        return render_template('characters.html', char_names = char_names)


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

        flash(error)
        return render_template('char.html', content = char_json, timestamp = creation_time)


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

def get_char_personal_gear_items(api_wrapper, char_string, char_values):
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

    return personal_gear_items
