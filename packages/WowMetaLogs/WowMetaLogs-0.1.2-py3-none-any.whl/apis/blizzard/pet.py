###########
# Imports #
###########

from blizzard import apirequest


###########
# Pet API #
###########


def get_master_list():
    rq = apirequest.ApiRequest('pet/')
    return apirequest.make_request(rq)


def get_ability(abilityid):
    rq = apirequest.ApiRequest('pet/abilities/' + abilityid)
    return apirequest.make_request(rq)


def get_species(speciesid):
    rq = apirequest.ApiRequest('pet/species/' + speciesid)
    return apirequest.make_request(rq)


def get_stats(speciesid, level=1, breedId=5, qualityId=1):
    rq = apirequest.ApiRequest('pet/stats/' + speciesid)
    rq.add_option('level', level)
    rq.add_option('breedId', breedId)
    rq.add_option('qualityId', qualityId)
    return apirequest.make_request(rq)
