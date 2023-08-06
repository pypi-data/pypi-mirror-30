import dataresources

classes = dataresources.get_character_classes()
talents = dataresources.get_talents()

for value in classes['classes']:
    print(value)
    for spec in talents[str(value['id'])]['specs']:
        print('\t' + str(spec))