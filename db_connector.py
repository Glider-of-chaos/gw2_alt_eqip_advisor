import configparser
import mysql.connector
import os
import importlib.util
import pdb

current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
personal_config = configparser.ConfigParser()
personal_config.read(config_path)

exceptions_path = os.path.join(current_dir, 'exceptions.py')
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path)
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)

class DBConnector():
    def __init__(self):
        self.connection_details = {'host': personal_config['DB']['host'],
                'port': int(personal_config['DB']['port']),
                'user': personal_config['DB']['user'],
                'password': personal_config['DB']['passwd'],
                'database': personal_config['DB']['db'],}

    def test_insert(self):
        pass
        #self.curs.execute("insert into characters (char_name, char_json) values ('test_name', '{tst:json}')")

    def get_item_json(self, item_id):
        connection = mysql.connector.connect(**self.connection_details)
        cursor = connection.cursor()

        item_select = "SELECT item_json FROM items WHERE item_id = {0}".format(item_id)
        cursor.execute(item_select)
        select_result = cursor.fetchall()
        #pdb.set_trace()
        row_count = cursor.rowcount
        if row_count == 1:
            item_json = select_result[0][0].decode()
            connection.close()
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

        item_insert = ('INSERT INTO items (item_id, item_json) VALUES (%s, %s)')
        #pdb.set_trace()

        cursor.execute(item_insert, item_data)
        connection.close()

