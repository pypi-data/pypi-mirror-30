###########
# Imports #
###########

from blizzard import apirequest
from urllib import request
import json


###############
# Auction API #
###############

def get_auction_data_status(realm):
    rq = apirequest.ApiRequest('auction/data/' + realm)
    return apirequest.make_request(rq)


# Must get url from get_auction_data_status()
def get_auction_data(url):
    with request.urlopen(url) as req:
        return json.loads(req.read().decode())
