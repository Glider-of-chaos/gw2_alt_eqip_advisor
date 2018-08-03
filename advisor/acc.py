import functools

from flask import (Blueprint, flash, g, redirect, render_template, request, session, url_for)

from .db_connector import get_db

key_blueprint = Blueprint('key', __name__, url_prefix = '/api_key')

@key_blueprint.route('/set', methods = ('GET', 'POST'))
def set_api_key():
    if request.method == 'POST':
        api_key = request.form['api_key']
        #db = get_db
        error = None

        if not api_key:
            error = 'API key is required'
        else:
            session.clear()
            session['api_key'] = api_key
            return redirect(url_for('chars.char_list'))

        flash(error)

    return render_template('api_key.html')

@key_blueprint.before_app_request
def load_api_key():
    g.api_key = session.get('api_key')
