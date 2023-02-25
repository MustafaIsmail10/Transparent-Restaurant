import json
from exceptions import *

# This function transforms the python dictionary to json
def responseFormatter(raw_response):
    """
    Put a dictionary in an appropriate formant for response
    """
    body = json.dumps(raw_response, indent=2) + "\n"
    response = (len(body), body)
    return response


def is_vegan(database, meal):
    """
    Checks if a meal is vegan
    """
    is_vegan = True
    for ing in meal["ingredients"]:
        for ingData in database["ingredients"]:
            if ing["name"] == ingData["name"]:
                if "vegan" not in ingData["groups"]:
                    is_vegan = False
                break

    return is_vegan


def is_vegetarian(database, meal):
    """
    Checks if a meal is vegetarian
    """
    is_vegetarian = True
    for ing in meal["ingredients"]:
        for ingData in database["ingredients"]:
            if ing["name"] == ingData["name"]:
                if "vegetarian" not in ingData["groups"]:
                    is_vegetarian = False

                break

    return is_vegetarian


def getMeal(database, id):
    """
    Get the database and an id of a meal and sends the meal back
    """
    item = [meal for meal in database["meals"] if meal["id"] == id]
    if item == []:
        raise MissingInDatabase(
            "There is no meal with the passed id in the database. Please pass an id with a proper id"
        )
    return item[0]
