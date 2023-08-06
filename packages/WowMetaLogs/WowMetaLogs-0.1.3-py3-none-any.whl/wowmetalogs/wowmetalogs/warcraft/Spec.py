###########
# Imports #
###########




##############
# Spec Class #
##############


class Spec:

    def __init__(self, spec_json):
        self.json = spec_json

    def __str__(self):
        return self.get_name()

    def get_name(self):
        return self.json['name']

    def get_role(self):
        return self.json['role']
