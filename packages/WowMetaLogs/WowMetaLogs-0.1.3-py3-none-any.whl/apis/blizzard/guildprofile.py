###########
# Imports #
###########

from blizzard import apirequest


#####################
# Guild Profile API #
#####################


def get_guild_profile(realm, guildname, fields=None):
    rq = apirequest.ApiRequest('guild/{}/{}'.format(realm, guildname))
    if fields is not None:
        rq.add_option('fields', fields)
    return apirequest.make_request(rq)


def get_members(realm, guildname):
    return get_guild_profile(realm, guildname, 'members')


def get_achievements(realm, guildname):
    return get_guild_profile(realm, guildname, 'achievements')


def get_news(realm, guildname):
    return get_guild_profile(realm, guildname, 'news')


def get_challenge(realm, guildname):
    return get_guild_profile(realm, guildname, 'challenge')
