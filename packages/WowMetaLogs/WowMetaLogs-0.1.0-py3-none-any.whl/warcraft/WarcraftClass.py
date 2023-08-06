###########
# Imports #
###########

from apis.blizzard import dataresources
from warcraft.Spec import Spec


#############
# Constants #
#############

__ALL_CLASSES__ = {}


def get_class(class_name):
    return __ALL_CLASSES__[class_name]


##################
# Warcraft Class #
##################

class WarcraftClass:

    def __init__(self, class_json):
        self.json = class_json
        self.name = self.json['name']
        self.power_type = self.json['powerType']
        self.id = self.json['id']
        self.specs = {}

    def get_name(self):
        return self.name

    def get_power_type(self):
        return self.power_type

    def get_id(self):
        return self.id

    def add_spec(self, spec):
        self.specs[spec.get_name()] = spec

    def get_spec(self, spec_name):
        return self.specs[spec_name]

    def get_all_specs(self):
        return self.specs()


#########
# Setup #
#########


def setup():
    # Make API Calls for Class and Talent data
    classes_json = dataresources.get_character_classes()
    talents_json = dataresources.get_talents()

    # Create Classes
    for class_json in classes_json['classes']:
        new_class = WarcraftClass(class_json)
        # Add Specs
        for spec_json in talents_json[str(new_class.get_id())]['specs']:
            new_class.add_spec(Spec(spec_json))
        __ALL_CLASSES__[new_class.get_name()] = new_class
        __ALL_CLASSES__[new_class.get_id()] = new_class
