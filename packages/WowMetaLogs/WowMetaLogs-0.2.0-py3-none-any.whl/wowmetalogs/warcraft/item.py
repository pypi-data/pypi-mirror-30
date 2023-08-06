##############
# Item Class #
##############


class Item:

    def __init__(self, item_json):
        self.json = item_json

    def __str__(self):
        return "({}) {}".format(self.json['id'], self.json['name'])

    def get_id(self):
        return self.json['id']

    def get_name(self):
        return self.json['name']

    def get_description(self):
        return self.json['description']

    def get_bonus_list(self):
        return self.json['bonusLists']

    def get_context(self):
        return self.json['context']

