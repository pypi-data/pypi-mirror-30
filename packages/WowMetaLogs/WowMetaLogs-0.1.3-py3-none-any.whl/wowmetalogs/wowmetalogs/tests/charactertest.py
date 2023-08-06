###########
# Imports #
###########

from wowmetalogs.warcraft import Character


##################
# Character Test #
##################

piousbob = Character("Piousbob", "Proudmoore")

print(piousbob)
print(piousbob.get_current_spec())
for talent in piousbob.get_talents_by_spec(piousbob.get_current_spec()):
    print(talent)
