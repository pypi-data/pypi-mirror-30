###########
# Imports #
###########

from blizzard import apirequest


####################
# Realm Status API #
####################


def get_realm_status():
    rq = apirequest.ApiRequest('realm/status')
    return apirequest.make_request(rq)
