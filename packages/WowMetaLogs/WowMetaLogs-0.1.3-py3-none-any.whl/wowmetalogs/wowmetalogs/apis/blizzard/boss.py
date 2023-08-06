###########
# Imports #
###########

from blizzard import apirequest


############
# Boss API #
############

def get_master_list():
    rq = apirequest.ApiRequest('boss/')
    return apirequest.make_request(rq)


def get_boss(boss_id):
    rq = apirequest.ApiRequest('boss/' + boss_id)
    return apirequest.make_request(rq)
