##############
# Zone Class #
##############


class Encounter:

    def __init__(self, encounter):
        self.id = encounter["id"]
        self.name = encounter["name"]

    def __str__(self):
        return "(ID: " + str(self.id) + ") " + self.name
