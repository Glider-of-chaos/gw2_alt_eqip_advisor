import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)
from flask import Flask
#from werkzeug.security import check_password_hash, generate_password_hash

#from eq_advisor.db_connector import get_db
from .db_connector import get_db

app = Flask(__name__)

char_blueprint = Blueprint('chars', __name__, url_prefix = '/char')

@char_blueprint.route('/<char_name>', methods = ('GET', ))
@app.route('/<char_name>')
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
