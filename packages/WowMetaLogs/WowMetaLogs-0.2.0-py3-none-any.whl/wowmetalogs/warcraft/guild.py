###########
# Imports #
###########

from warcraft import character, achievement, item


###############
# Guild Class #
###############


class Guild:

    def __init__(self, guild_json):
        self.json = guild_json
        self.roster = {}

    def __str__(self):
        return

    def get_name(self):
        return self.json['name']

    def get_realm(self):
        return self.json['realm']

    def get_level(self):
        return self.json['level']

    def get_achievement_points(self):
        return self.json['achievementPoints']

    def get_news(self):
        return self.json['news']

    def get_members(self):
        return self.json['members']

    def get_member(self, char_name):
        return self.roster[char_name].char

    def get_player_rank(self, char_name):
        return self.roster[char_name].rank