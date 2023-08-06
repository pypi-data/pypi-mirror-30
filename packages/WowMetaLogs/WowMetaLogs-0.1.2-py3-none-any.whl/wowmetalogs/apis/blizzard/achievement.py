###########
# Imports #
###########

from blizzard import apirequest


###################
# Achievement API #
###################


def get_achievement(achievementid):
    rq = apirequest.ApiRequest('auction/data/' + achievementid)
    return apirequest.make_request(rq)
