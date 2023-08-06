#####################
# Achievement Class #
#####################


class Achievement:

    def __init__(self, achievement_json):
        self.json = achievement_json

    def __str__(self):
        return '({}) {}'.format(self.json['id'], self.json['title'])

    def get_id(self):
        return self.json['id']

    def get_title(self):
        return self.json['title']

    def get_points(self):
        return self.json['points']

    def get_description(self):
        return self.json['description']

    def get_reward(self):
        return self.json['reward']

    def get_reward_items(self):
        # TODO: Need to fill out Item class first
        pass

    def get_icon(self):
        return self.json['icon']

    def get_criteria(self):
        return self.json['criteria']

    def is_account_wide(self):
        return self.json['accountWide']

    def get_faction_id(self):
        return self.json['factionId']


#####################
# Achievement Cache #
#####################

All_Achievements = {
    # Key - Achievement ID
    # Value - Achievement
}


def get_achievement(achievement_id):
    return All_Achievements[achievement_id]


def achievement_exists(achievement_id):
    return achievement_id in All_Achievements


def create_new_achieve(achievement_json):
    achieve = Achievement(achievement_json)
    All_Achievements[achieve.get_id()] = achieve
    return achieve
