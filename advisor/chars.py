import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flask import Flask

from .db_connector import get_db

char_blueprint = Blueprint('chars', __name__, url_prefix = '/char')


@char_blueprint.route('/list', methods = ('GET', ))
def char_list():
    if request.method == 'GET':
        db = get_db
        error = None
        return render_template('char.html', content = "char list")



@char_blueprint.route('/<char_name>', methods = ('GET', ))
def char(char_name):
    if request.method == 'GET':
        db = get_db()
        error = None

        char_row = db.execute(f"SELECT json_string FROM `character` WHERE id = '{char_name}'").fetchone()
        char_json = char_row[0]


        if char_json is None:
            error = 'Character not found'

        flash(error)
        return render_template('char.html', content = char_json)
