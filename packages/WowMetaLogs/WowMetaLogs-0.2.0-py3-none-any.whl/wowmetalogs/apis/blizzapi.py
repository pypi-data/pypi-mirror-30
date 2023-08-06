###########
# Imports #
###########

import requests
import json
from warcraft import achievement, character, item, guild

###################
# Blizz API Class #
###################


class BlizzAPI:

    def __init__(self, apikey):
        self.apikey = apikey
        self.host = 'https://us.api.battle.net/wow/'

    def make_api_request(self, request_path, request_options={}):
        options = request_options
        options['apikey'] = self.apikey
        options['locale'] = 'en_US'
        req = requests.get(self.host + request_path, params=options)
        return json.loads(req.text)

    def get_achievement(self, achievement_id):
        return self.make_api_request('achievement/'+str(achievement_id))

    def get_auction_data_status(self, realm, fields={}):
        return self.make_api_request('auction/data/' + realm, fields)

    def get_boss(self, boss_id, fields={}):
        return self.make_api_request('boss/' + str(boss_id), fields)

    def get_boss_master_list(self, fields={}):
        return self.make_api_request('boss/', fields)

    def get_challenge_mode_leaderboard(self, realm, fields={}):
        return self.make_api_request('challenge/' + realm, fields)

    def get_challenge_mode_leaderboard_region(self, fields={}):
        return self.make_api_request('challenge/region', fields)

    def get_character(self, realm, name):
        fields = 'achievements,appearance,feed,guild,hunterPets,items,mounts,pets,petSlots,professions,'
        fields += 'progression,pvp,quests,reputation,statistics,stats,talents,titles,audit'
        return self.make_api_request('character/{}/{}'.format(realm,name), {'fields': fields})

    def get_guild(self, realm, name):
        print('Creating guild {} of {}...'.format(name, realm))
        fields = {
            'fields': 'members,news,achievements,challenge'
        }
        return self.make_api_request('guild/'+realm+'/'+name, fields)

    def get_item(self, item_id, context=None, fields={}):
        req_url = 'item/' + str(item_id)
        if not context:
            req_url += '/' + context
        return self.make_api_request(req_url, fields)

    def get_item_set(self, set_id, fields={}):
        return self.make_api_request('item/set/' + set_id, fields)

    def get_mount_master_list(self, fields={}):
        return self.make_api_request('mount/', fields)

    def get_pet_master_list(self, fields={}):
        return self.make_api_request('pet/', fields)

    def get_pet_ability(self, ability_id, fields={}):
        return self.make_api_request('pet/ability'+str(ability_id), fields)

    def get_pet_species(self, species_id, fields={}):
        return self.make_api_request('pet/species/'+str(species_id), fields)

    def get_pvp_leaderboards(self, bracket, fields={}):
        return self.make_api_request('leaderboard/' + bracket, fields)

    def get_quest(self, quest_id, fields={}):
        return self.make_api_request('quest/'+str(quest_id), fields)

    def get_realm_status(self, realms=''):
        fields = {}
        if realms:
            fields = {'realms': realms}
        return self.make_api_request('realm/status', fields)

    def get_recipe(self, recipe_id, fields={}):
        return self.make_api_request('recipe/'+str(recipe_id), fields)

    def get_spell(self, spell_id, fields={}):
        return self.make_api_request('spell/'+str(spell_id), fields)

    def get_zone_master_list(self):
        return self.make_api_request('zone/')

    def get_zone(self, zone_id, fields={}):
        return self.make_api_request('zone'+str(zone_id), fields)

    def get_data_battlegroups(self):
        return self.make_api_request('data/battlegroups/')

    def get_data_char_races(self):
        return self.make_api_request('data/character/races')

    def get_data_char_classes(self):
        return self.make_api_request('data/character/classes')

    def get_data_char_achievements(self):
        return self.make_api_request('data/character/achievements')

    def get_data_guild_rewards(self):
        return self.make_api_request('data/guild/rewards')

    def get_data_guild_perks(self):
        return self.make_api_request('data/guild/perks')

    def get_data_guild_achievements(self):
        return self.make_api_request('data/guild/achievements')

    def get_data_item_classes(self):
        return self.make_api_request('data/item/classes')

    def get_data_talents(self):
        return self.make_api_request('data/talents')

    def get_data_pet_types(self):
        return self.make_api_request('data/pet/types')
