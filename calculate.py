from exceptions import *


def qualityCalculator(meal, body):
    qualityScore = 0
    ingNum = 0
    for ing in meal["ingredients"]:
        ingNum += 1
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
    return quality


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

    return total_price


def calculateCostsOfIngredient(ing, database):
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


def calculateIngredientMinCost(ing, database):
    costs = calculateCostsOfIngredient(ing, database)
    minimum = costs[0]
    if costs[1][0] < costs[0][0]:
        minimum = costs[1]
    elif costs[2][0] < costs[0][0]:
        minimum = costs[2]
    return minimum


def calculateMinOfMeal(database, meal):
    minCost = 0
    for ing in meal["ingredients"]:
        minCost += calculateIngredientMinCost(ing, database)[0]
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
