###########
# Imports #
###########

from blizzard import apirequest


##############
# Recipe API #
##############


def get_recipe(recipe_id):
    rq = apirequest.ApiRequest('recipe/' + recipe_id)
    return apirequest.make_request(rq)
