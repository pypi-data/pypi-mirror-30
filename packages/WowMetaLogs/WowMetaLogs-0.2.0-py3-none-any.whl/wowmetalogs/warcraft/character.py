###########
# Imports #
###########

from warcraft.item import Item


###################
# Character Class #
###################


class Character:

    def __init__(self, char_json):
        self.json = char_json
        if 'name' in self.json:
            self.exists = True
        else:
            self.exists = False
            return
        try:
            self.items = self.parse_items(self.json['items'])
        except KeyError:
            print('KeyError')
            print(self.json)

    def __str__(self):
        return '{} of {}'.format(self.get_name(), self.get_realm())

    def get_name(self):
        return self.json['name']

    def get_realm(self):
        return self.json['realm']

    def get_item_level(self):
        return self.json['items']['averageItemLevel']

    def get_item_level_equipped(self):
        return self.json['items']['averageItemLevelEquipped']

    def parse_items(self, items_json):
        items = {}
        for key, value in items_json.items():
            if 'averageItemLevel' not in key:
                items[key] = Item(value)
        return items

    def get_feed(self):
        return self.json['feed']
