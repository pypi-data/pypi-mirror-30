###########
# Imports #
###########

from blizzard import apirequest


############
# Zone API #
############


def get_master_list():
    rq = apirequest.ApiRequest('zone/')
    return apirequest.make_request(rq)


def get_zone(zoneid):
    rq = apirequest.ApiRequest('zone/' + zoneid)
    return apirequest.make_request(rq)
