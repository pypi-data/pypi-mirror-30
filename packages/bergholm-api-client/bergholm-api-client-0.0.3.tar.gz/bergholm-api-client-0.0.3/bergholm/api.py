import urllib2
import urllib
import re
import json

import requests

from expections import DoesNotExist

class Client:
    def __init__(self, access_token):
        self.access_token = access_token
        self.base_url = 'https://api.bergholmcdn.com/v1'

    def build_url(self, uris=[]):
        uri = '/'.join(str(uri) for uri in uris)
        return '{}/{}'.format(self.base_url, uri)

    def get(self, uris):
        url = self.build_url(uris)
        response = requests.get(url, headers={'Authorization': 'Bearer {}'.format(self.access_token)})
        status_code = response.status_code

        if status_code == 200:
            return response.json()

        raise DoesNotExist('We could not process the request ({}, {}).'.format(url, status_code))

    def get_caravans(self):
        return self.get(['caravans'])

    def get_caravan(self, caravan_slug):
        return self.get(['caravans', caravan_slug])

    def get_caravan_family(self, caravan_slug, family_slug):
        return self.get(['caravans', caravan_slug, family_slug])

    def get_caravan_family_model(self, caravan_slug, family_slug, model_slug):
        return self.get(['caravans', caravan_slug, family_slug, model_slug])

    def get_motorhomes(self):
        return self.get(['motorhomes'])

    def get_motorhome(self, motorhome_slug):
        return self.get(['motorhomes', motorhome_slug])

    def get_motorhome_family(self, motorhome_slug, family_slug):
        return self.get(['motorhomes', motorhome_slug, family_slug])

    def get_motorhome_family_model(self, motorhome_slug, family_slug, model_slug):
        return self.get(['motorhomes', motorhome_slug, family_slug, model_slug])