import configparser
#import mysql.connector
import os
import importlib.util
import pdb
import sqlite3
import click

from flask import current_app, g
from flask.cli import with_appcontext

def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(
                current_app.config['DATABASE'],
                detect_types = sqlite3.PARSE_DECLTYPES
                )
        g.db.row_factory = sqlite3.Row

    return g.db

def close_db(e = None):
    db = g.pop('db', None)

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode())


@click.command('init-db')
@with_appcontext
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)



current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
personal_config = configparser.ConfigParser()
personal_config.read(config_path)

exceptions_path = os.path.join(current_dir, 'exceptions.py')
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path)
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)

class DBConnector():
    #def __init__(self):
        #self.connection_details = {'host': personal_config['DB']['host'],
                #'port': int(personal_config['DB']['port']),
                #'user': personal_config['DB']['user'],
                #'password': personal_config['DB']['passwd'],
                #'database': personal_config['DB']['db'],}

    def test_insert(self):
        pass
        #self.curs.execute("insert into characters (char_name, char_json) values ('test_name', '{tst:json}')")

    def get_item_json(self, item_type, item_id):
        #connection = mysql.connector.connect(**self.connection_details)
        connection = get_db()
        cursor = connection.cursor()

        item_select = "SELECT json_string FROM `{0}` WHERE id = '{1}'".format(item_type, item_id)
        cursor.execute(item_select)
        select_result = cursor.fetchall()
        #pdb.set_trace()
        row_count = len(select_result)
        if row_count == 1:
            item_json = select_result[0][0]
            #connection.close()
        elif row_count == 0:
            connection.close()
            raise exceptions.NoDBItemError(item_id)
        else:
            connection.close()
            raise exceptions.MultiplesWnenExpectingSingletonDBError(item_select)

        return item_json

    def add_item(self, item_id, item_json):
        connection = mysql.connector.connect(**self.connection_details)
        cursor = connection.cursor()
        item_data = (item_id, str(item_json))

        item_insert = ('INSERT INTO item (id, json_string) VALUES (%s, %s)')
        #pdb.set_trace()

        cursor.execute(item_insert, item_data)
        connection.close()

