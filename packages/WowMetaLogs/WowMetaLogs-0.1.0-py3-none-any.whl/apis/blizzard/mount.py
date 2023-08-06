###########
# Imports #
###########

from blizzard import apirequest


#############
# Mount API #
#############


def get_master_list():
    rq = apirequest.ApiRequest('mount/')
    return apirequest.make_request(rq)