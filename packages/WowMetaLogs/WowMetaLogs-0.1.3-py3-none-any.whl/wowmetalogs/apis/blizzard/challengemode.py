###########
# Imports #
###########

from blizzard import apirequest


######################
# Challenge Mode API #
######################

def get_realm_leaderboard(realm):
    rq = apirequest.ApiRequest('challenge/' + realm)
    return apirequest.make_request(rq)


def get_region_leaderboard():
    return get_realm_leaderboard('region')
