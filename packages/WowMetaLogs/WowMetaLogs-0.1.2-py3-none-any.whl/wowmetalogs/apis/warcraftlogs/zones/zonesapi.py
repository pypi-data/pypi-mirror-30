###########
# Imports #
###########

from urllib import request
import json
from .zone import Zone


################
# API Function #
################

class Zones:

    def __init__(self, apikey):
        self.site = "https://www.warcraftlogs.com:443/v1/zones?api_key=" + apikey
        self.zones = self.requestzones()

    def requestzones(self):
        with request.urlopen(self.site) as url:
            data = json.loads(url.read().decode())
        return [Zone(zone["id"], zone["name"], zone["encounters"]) for zone in data]

    def getzones(self):
        if self.zones == None:
            self.zones = self.requestzones()
        return self.zones

    def getzone(self, searchstring):
        for zone in self.zones:
            if searchstring in zone.name:
                return zone


