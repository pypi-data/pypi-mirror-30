###########
# Imports #
###########

from urllib import request
import json


###################
# Constant Values #
###################

__wlurl__ = "https://www.warcraftlogs.com:443/v1/"  # WarcraftLogs site URL
__apikey__ = "?api_key=0bc8270ef0f815fa02672adfe3c969dc"     # WarcraftLogs API Key


###########
# Classes #
###########

def getclasses():
    '''
    Gets an array of Class objects. Each Class corresponds to a class in the game
    :return: JSON object of the request data
    '''
    return wlrequest("classes")


##########
# Parses #
##########


############
# Rankings #
############

class RankingsSearchOptions(object):

    encounterID = None
    metric = None
    size = None
    difficulty = None
    partition = None
    charclass = None
    charspec = None
    bracket = None
    limit = None
    guild = None
    server = None
    region = None
    page = None
    filter = None


##########
# Report #
##########


###########
# Reports #
###########


#########
# Zones #
#########

def getzones():
    '''
    Gets an array of Zone objects. Each zones corresponds to a raid/dungeon 
    instance in the game and has its own set of encounters.
    :return: JSON object of the requested data
    '''
    return wlrequest("zones")


####################
# Helper Functions #
####################

def wlrequest( urlpartial ):
    '''
    Makes a request to the warcraftlogs api
    :param urlpartial: the request being made
    :return: JSON object of the requested data
    '''
    with request.urlopen( __wlurl__ + urlpartial + __apikey__ ) as url:
        data = json.load(url.read().decode())
    return data
