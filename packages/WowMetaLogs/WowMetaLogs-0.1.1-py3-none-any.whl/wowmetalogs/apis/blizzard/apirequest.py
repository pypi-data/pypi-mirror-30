###########
# Imports #
###########

from urllib import request
import json

#############
# Constants #
#############

BLIZZ_API_SITE = 'https://us.api.battle.net/wow/'
BLIZZ_API_KEY = 'j2g3d863c73ujzd2jdc8dfg73m75zr4g'


#############
# Blizz API #
#############


def make_request(api_request):
    with request.urlopen(BLIZZ_API_SITE + api_request.get_request()) as url:
        return json.loads(url.read().decode())


class ApiRequest:

    def __init__(self, req_type, locale='en_US'):
        self.type = req_type
        self.options = {'locale': locale, 'apikey': BLIZZ_API_KEY}

    def add_option(self, key, value):
        self.options[key] = value

    def get_request(self):
        request_url = self.type + '?'
        for key, value in self.options.items():
            request_url += '{}={}&'.format(key, str(value))
        return request_url[:-1]
