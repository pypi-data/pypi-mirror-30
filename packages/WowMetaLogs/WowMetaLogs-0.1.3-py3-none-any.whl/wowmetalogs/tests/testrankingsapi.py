from warcraftlogs.zones.zonesapi import Zones
from warcraftlogs.rankings.rankingsapi import Rankings
from reporting.Character import Character

apikey = "0bc8270ef0f815fa02672adfe3c969dc"

zones = Zones(apikey)
rankings = Rankings(apikey)

char = Character("correlia","proudmoore","us")
ranks = char.getrankingsforencounter("2092",rankings)
specranks = char.sortbyspec(1,ranks)
for spec in specranks:
    perc = 1 - spec["rank"] / spec["outOf"]
    print(str(perc*100)[:2])
