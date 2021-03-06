import json
import urllib.request
import importlib.util
import os
import configparser
import pdb

# TODO: remake next line. it's godawful
current_dir = os.path.split(os.path.realpath(__file__))[0]
config_path = os.path.join(current_dir, 'personal.ini')
personal_config = configparser.ConfigParser()
personal_config.read(config_path)

exceptions_path = os.path.join(current_dir, 'exceptions.py')
spec = importlib.util.spec_from_file_location("exceptions", exceptions_path)
exceptions = importlib.util.module_from_spec(spec)
spec.loader.exec_module(exceptions)

class ApiWrapper(object):

    base_api_url = "https://api.guildwars2.com/v2"
    token = ""

    def __init__(self, token):
        self.token = token
    
    def get_json_string(self, endpoint, requested_id = ""):

        if endpoint == 'item':
            request_url = "{0}/items/{1}".format(self.base_api_url, requested_id)
            #pdb.set_trace()
        elif endpoint == 'character':
            request_url = "{0}/characters/{1}?access_token={2}".format(self.base_api_url, requested_id, self.token)
        elif endpoint == 'characters':
            request_url = "{0}/characters?access_token={1}".format(self.base_api_url, self.token)
        elif endpoint == 'bank':
            request_url = "{0}/account/bank?access_token={1}".format(self.base_api_url, self.token)


        #pdb.set_trace()
        try:
            with urllib.request.urlopen(request_url) as response:
                if response.getcode() == 200:
                    response_string = response.read().decode()
                    #response_json = json.loads(response_string)
                    return response_string
                else:
                    raise exceptions.ApiConnectionError(request_link, response.getcode())
        except urllib.error.HTTPError as err:
            print("got an error trying to get item, error message {0}".format(err))
            return None
