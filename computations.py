from exceptions import *
from func import *


def qualityCalculator(meal, body):
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
