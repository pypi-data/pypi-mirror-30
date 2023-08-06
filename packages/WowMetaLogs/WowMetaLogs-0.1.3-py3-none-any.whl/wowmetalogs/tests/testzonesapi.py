from warcraftlogs.zones.zonesapi import Zones

__apikey__ = "0bc8270ef0f815fa02672adfe3c969dc"     # WarcraftLogs API Key

zones = Zones(__apikey__)

antorus = zones.getzone("Antorus")

print(antorus.getnicestring())
