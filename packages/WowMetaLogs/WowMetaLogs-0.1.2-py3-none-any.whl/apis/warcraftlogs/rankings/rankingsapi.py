###########
# Imports #
###########


from urllib import request
import json


################
# API Function #
################

class Rankings:

    def __init__(self, wlapikey):
        self.apikey = "api_key=" + wlapikey
        self.site = "https://www.warcraftlogs.com:443/v1/"
        self.rankings = {}

    def formatrequesturl(self, requeststring):
        rq = self.site + requeststring + self.apikey
        print(rq)
        return rq

    def getrankings(self, requesturl):
        if requesturl in self.rankings:
            return self.rankings[requesturl]
        with request.urlopen(requesturl) as url:
            rankings = json.loads(url.read().decode())
        self.rankings[requesturl] = rankings
        return rankings

    def getcharacterrankings(self, charactername, servername, region,encounterid, **kwargs):
        requesturl = "rankings/character/"
        requesturl += charactername + "/"
        requesturl += servername + "/"
        requesturl += region + ""
        requesturl += "?encounter=" + encounterid + "&"
        if "zoneid" in kwargs:
            requesturl += "?zone=" + kwargs["zoneid"] + "&"
        if "metric" in kwargs:
            requesturl += "?metric=" + kwargs["metric"] + "&"
        if "bracket" in kwargs:
            requesturl += "?bracket=" + kwargs["bracket"] + "&"
        if "partition" in kwargs:
            requesturl += "?partition=" + kwargs["partition"] + "&"
        return self.getrankings(self.formatrequesturl(requesturl))

    def getencounterrankings(self):
        requesturl = ""
        return self.getrankings(requesturl)
