###########
# Imports #
###########

import characterprofile
from wowmetalogs.warcraft import WarcraftClass


###################
# Character Class #
###################


class Character:

    def __init__(self, name, realm):
        self.json = characterprofile.get_talents(realm, name)

        # Get Char's Class
        self.warcraft_class = WarcraftClass.get_class(self.json['class'])
        self.talents = self.json['talents']

    def __str__(self):
        return "{} - {} {}".format(self.json['name'], self.get_current_spec().get_name(), self.get_class_name())

    def get_role(self):
        return self.get_current_spec().get_role()

    def get_name(self):
        return self.json['name']

    def get_class_name(self):
        return self.warcraft_class.get_name()

    def get_spec_name(self):
        return

    def get_current_spec(self):
        for talent in self.talents:
            if 'selected' in talent:
                return self.warcraft_class.get_spec(talent['spec']['name'])

    def get_all_specs(self):
        return self.warcraft_class.get_all_specs()

    def get_talents_by_spec(self, spec):
        for talent in self.talents:
            if talent['spec']['name'] == spec.get_name():
                return talent['talents']
