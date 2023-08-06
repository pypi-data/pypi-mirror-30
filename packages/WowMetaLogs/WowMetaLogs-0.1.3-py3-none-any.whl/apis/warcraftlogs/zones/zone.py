###########
# Imports #
###########


from .encounter import Encounter


##############
# Zone Class #
##############


class Zone:

    def __init__(self, zoneid, zonename, encounterlist):
        self.id = zoneid
        self.name = zonename
        self.encounters = [Encounter(encounter) for encounter in encounterlist]

    def __str__(self):
        return self.name + " (Zone ID: " + str(self.id) + ")"

    def getnicestring(self):
        nicestring = str(self)
        for encounter in self.encounters:
            nicestring += "\n\t" + str(encounter)
        return nicestring
