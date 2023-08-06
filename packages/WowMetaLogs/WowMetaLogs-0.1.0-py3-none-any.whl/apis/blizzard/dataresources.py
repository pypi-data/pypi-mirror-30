###########
# Imports #
###########

from blizzard import apirequest


######################
# Data Resources API #
######################


def get_data(data_str):
    rq = apirequest.ApiRequest('data/' + data_str)
    return apirequest.make_request(rq)


def get_battlegroups():
    return get_data('battlegroups/')


def get_character_races():
    return get_data('character/races')


def get_character_classes():
    return get_data('character/classes')


def get_character_achievements():
    return get_data('character/achievements')


def get_guild_rewards():
    return get_data('guild/rewards')


def get_guild_perks():
    return get_data('guild/perks')


def get_guild_achievements():
    return get_data('guild/achievements')


def get_item_classes():
    return get_data('item/classes')


def get_talents():
    return get_data('talents')


def get_pet_types():
    return get_data('pet/types')
