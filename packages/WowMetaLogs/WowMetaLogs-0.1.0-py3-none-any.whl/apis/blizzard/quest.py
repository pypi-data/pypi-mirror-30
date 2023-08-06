###########
# Imports #
###########

from blizzard import apirequest


#############
# Quest API #
#############


def get_quest(questid):
    rq = apirequest.ApiRequest('quest/' + questid)
    return apirequest.make_request(rq)
