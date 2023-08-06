###########
# Imports #
###########

from blizzard import apirequest


#########################
# Character Profile API #
#########################

def get_character_profile(realm, charname, fields=None):
    rq = apirequest.ApiRequest('character/{}/{}'.format(realm, charname))
    if fields is not None:
        rq.add_option('fields', fields)
    return apirequest.make_request(rq)


def get_achievements(realm, charname):
    return get_character_profile(realm, charname, "achievements")


def get_appearance(realm, charname):
    return get_character_profile(realm, charname, "appearance")


def get_feed(realm, charname):
    return get_character_profile(realm, charname, "feed")


def get_guild(realm, charname):
    return get_character_profile(realm, charname, "guild")


def get_hunter_pets(realm, charname):
    return get_character_profile(realm, charname, "hunterPets")


def get_items(realm, charname):
    return get_character_profile(realm, charname, "items")


def get_mounts(realm, charname):
    return get_character_profile(realm, charname, "mounts")


def get_pets(realm, charname):
    return get_character_profile(realm, charname, "pets")


def get_pet_slots(realm, charname):
    return get_character_profile(realm, charname, "petSlots")


def get_professions(realm, charname):
    return get_character_profile(realm, charname, "professions")


def get_pvp(realm, charname):
    return get_character_profile(realm, charname, "pvp")


def get_quests(realm, charname):
    return get_character_profile(realm, charname, "quests")


def get_reputation(realm, charname):
    return get_character_profile(realm, charname, "reputation")


def get_statistics(realm, charname):
    return get_character_profile(realm, charname, "statistics")


def get_stats(realm, charname):
    return get_character_profile(realm, charname, "stats")


def get_talents(realm, charname):
    return get_character_profile(realm, charname, "talents")


def get_titles(realm, charname):
    return get_character_profile(realm, charname, "titles")


def get_audit(realm, charname):
    return get_character_profile(realm, charname, "audit")
