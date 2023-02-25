from exceptions import *
import json, random


# This function transforms the python dictionary to json
def responseFormatter(raw_response):
    """
    Put a dictionary in an appropriate formant for response
    """
    body = json.dumps(raw_response, indent=2) + "\n"
    response = (len(body), body)
    return response


def isVegan(database, meal):
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


def isVegetarian(database, meal):
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


def qualityCalculator(meal, body):
    """Calculate the quality of a meal"""
    qualityScore = 0
    ingNum = len(meal["ingredients"])
    for ing in meal["ingredients"]:
        if ing["name"].lower() in body:
            if body[ing["name"].lower()] == "medium":
                qualityScore += 20
            elif body[ing["name"].lower()] == "low":
                qualityScore += 10
            else:
                qualityScore += 30
        else:
            qualityScore += 30
    quality = qualityScore / ingNum
    return round(quality, 2)


def priceCalulator(database, meal, body):
    """Calculate the price of a meal"""
    total_price = 0
    for ing in meal["ingredients"]:
        try:
            ingOptions = [
                ingOption
                for ingOption in database["ingredients"]
                if ing["name"] == ingOption["name"]
            ][0]["options"]
        except:
            raise RequiredParametersNotAvialble(
                "Problem with the database missing ingredients"
            )

        if ing["name"].lower() in body:
            if body[ing["name"].lower()] == "medium":
                total_price += 0.05
                total_price += (ing["quantity"] / 1000) * ingOptions[1]["price"]
            elif body[ing["name"].lower()] == "low":
                total_price += 0.1
                total_price += (ing["quantity"] / 1000) * ingOptions[2]["price"]
            else:
                total_price += (ing["quantity"] / 1000) * ingOptions[0]["price"]
        else:
            total_price += (ing["quantity"] / 1000) * ingOptions[0]["price"]
    return round(total_price, 2)


def getCostsOfIngredient(database, ing):
    """
    Calculates all costs of an Ingredient
    """
    try:
        ingOptions = [
            ingOption
            for ingOption in database["ingredients"]
            if ing["name"] == ingOption["name"]
        ][0]["options"]
    except:
        raise Exception()

    ingHighCost = (ing["quantity"] / 1000) * ingOptions[0]["price"]
    ingMediumCost = (ing["quantity"] / 1000) * ingOptions[1]["price"] + 0.05
    ingLowCost = (ing["quantity"] / 1000) * ingOptions[2]["price"] + 0.1

    return [(ingHighCost, "high"), (ingMediumCost, "medium"), (ingLowCost, "low")]


def getIngredientMinCost(database, ing):
    """
    Calculates the min cost of an ingredient and returns (<min cost>, <quality>)
    """
    costs = getCostsOfIngredient(database, ing)
    minimum = costs[0]
    for cost in costs:
        if cost[0] < minimum[0]:
            minimum = cost
    return minimum


def calculateMinOfMeal(database, meal):
    minCost = 0
    for ing in meal["ingredients"]:
        minCost += getIngredientMinCost(database, ing)[0]
    return minCost


def calculateMinPriceAllMeals(database):
    meals_min_cost = {}
    for meal in database["meals"]:
        try:
            meals_min_cost[meal["id"]] = calculateMinOfMeal(database, meal)
        except:
            continue
    return meals_min_cost


def allowedInBudgetMealsIds(budget, database):
    meals_min_cost = calculateMinPriceAllMeals(database)
    allowedMeals = []
    for meal_id in meals_min_cost:
        if meals_min_cost[meal_id] <= budget:
            allowedMeals.append(meal_id)
    return allowedMeals


def getMinCostAndOptionsOfMeal(database, meal):
    """
    Compute the min Cost of a meal and the options for that min cost and returns a tuple (<min costs>, <options>)
    """
    minCost = 0
    options = {}
    for ing in meal["ingredients"]:
        temp = getIngredientMinCost(database, ing)
        minCost += temp[0]
        options[ing["name"].lower()] = temp[1]
    return (minCost, options)


def getRandomOptionsWithinBudget(database, budget, meal):
    """
    choose random options for a meal within budget
    """
    currentCost = calculateMinOfMeal(database=database, meal=meal)
    options = {}
    for ing in meal["ingredients"]:
        costs = getCostsOfIngredient(database, ing)
        min_ing_cost = getIngredientMinCost(database, ing)
        new_config = random.choice(costs)
        if (currentCost - min_ing_cost[0] + new_config[0]) < budget:
            options[ing["name"].lower()] = new_config[1]
            currentCost = currentCost - min_ing_cost[0] + new_config[0]
        else:
            options[ing["name"].lower()] = min_ing_cost[1]
    return options
