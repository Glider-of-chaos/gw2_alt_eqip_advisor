import functools

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

        key_id = db.execute(f"SELECT id from api_key WHERE key_value = '{g.api_key}'").fetchone()

        chars = db.execute(f"SELECT id from character WHERE api_id = '{key_id[0]}'").fetchall()
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
