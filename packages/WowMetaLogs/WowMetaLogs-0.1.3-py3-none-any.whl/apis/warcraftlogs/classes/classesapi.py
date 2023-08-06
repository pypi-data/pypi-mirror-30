###########
# Imports #
###########

from urllib import request
import json
from .wowclass import WowClass


################
# API Function #
################

class Classes:

    def __init__(self, apikey):
        self.site = "https://www.warcraftlogs.com:443/v1/classes?api_key=" + apikey
        self.classes = self.requestclasses()

    def requestclasses(self):
        with request.urlopen(self.site) as url:
            data = json.loads(url.read().decode())
        return [WowClass(wowclass["name"], wowclass["id"], wowclass["specs"]) for wowclass in data]

    def getclasses(self):
        return self.classes

    def getclass(self, searchstring):
        for wowclass in self.classes:
            if searchstring in wowclass.name:
                return wowclass

