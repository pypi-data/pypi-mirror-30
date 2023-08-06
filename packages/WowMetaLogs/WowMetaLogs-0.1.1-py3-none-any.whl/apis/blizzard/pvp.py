###########
# Imports #
###########

from blizzard import apirequest


###########
# PVP API #
###########


def get_leaderboards(bracket):
    rq = apirequest.ApiRequest('leaderboards/' + bracket)
    return apirequest.make_request(rq)
