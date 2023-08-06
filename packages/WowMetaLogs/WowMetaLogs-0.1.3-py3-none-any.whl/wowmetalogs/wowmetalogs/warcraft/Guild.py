###########
# Imports #
###########




###############
# Guild Class #
###############


class Guild:

    def __init__(self, gname, gserver, gregion):
        self.name = gname
        self.server = gserver
        self.region = gregion
        self.roster = []

    def __str__(self):
        return "{} - {} ({})".format(self.name, self.server, self.region)

    def add_member(self, member):
        self.roster.append(member)

    def get_players(self, role):
        return [player for player in self.roster if player.get_role() == role]

    def get_tanks(self):
        return self.get_players('TANK')

    def get_healers(self):
        return self.get_players('HEALING')

    def get_dps(self):
        return self.get_players('DPS')

    def get_roster_composition(self):
        rostercomp = {}
        for player in self.roster:
            classname = player.get_class_name()
            if classname not in rostercomp:
                rostercomp[classname] = {}
                rostercomp[classname]['Total'] = 0
            classdict = rostercomp[classname]
            playerspec = player.get_spec()
            if playerspec not in classdict:
                classdict[playerspec] = 0
            classdict[playerspec] += 1
            classdict['Total'] += 1
        return rostercomp
