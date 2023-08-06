###########
# Imports #
###########

from blizzard import apirequest


############
# Item API #
############

def get_item(itemid):
    rq = apirequest.ApiRequest('item/' + itemid)
    return apirequest.make_request(rq)



def get_item_set(setid):
    rq = apirequest.ApiRequest('item/set/' + setid)
    return apirequest.make_request(rq)

