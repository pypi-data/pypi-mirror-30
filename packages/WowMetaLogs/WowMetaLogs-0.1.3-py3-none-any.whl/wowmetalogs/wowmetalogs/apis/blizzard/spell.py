###########
# Imports #
###########

from blizzard import apirequest


#############
# Spell API #
#############


def get_spell(spellid):
    rq = apirequest.ApiRequest('spell/' + spellid)
    return apirequest.make_request(rq)
