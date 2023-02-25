import socket, sys, json, math
from exceptions import *
import random
from computations import *
from func import *

# Getting and parsing the data base
file_path = "./data.json"
if len(sys.argv) == 2:
    file_path = sys.argv[1]

data_exist = False
database = {}

while not data_exist:
    try:
        data_file = open(file_path)
        database = json.load(data_file)
        data_file.close()
        data_exist = True
    except FileNotFoundError:
        data_exist = False
        file_path = input("Please give the right path to the database: ")


# Setting up the server socket
HOST = ""
PORT = 8080
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)
print("Listening on port %s ..." % PORT)


def listMealsHandler(requestData):
    """
    Handling list meals request
    """
    options = requestData["params"]
    try:
        is_vegeterian = options["is_vegetarian"]
    except:
        is_vegeterian = False

    try:
        is_vegan = options["is_vegan"]
    except:
        is_vegan = False

    ans = []
    if not is_vegan and not is_vegeterian:
        for meal in database["meals"]:
            item = {}
            item["id"] = meal["id"]
            item["name"] = meal["name"]
            item["ingredients"] = [ing["name"] for ing in meal["ingredients"]]
            ans.append(item)
    elif is_vegeterian:
        vegeterian_ingredients = [
            ing["name"]
            for ing in database["ingredients"]
            if "vegetarian" in ing["groups"]
        ]
        for meal in database["meals"]:
            is_vegeterian_meal = True
            for ing in meal["ingredients"]:
                if ing["name"] not in vegeterian_ingredients:
                    is_vegeterian_meal = False
                    break
            if not is_vegeterian_meal:
                continue

            item = {}
            item["id"] = meal["id"]
            item["name"] = meal["name"]
            item["ingredients"] = [ing["name"] for ing in meal["ingredients"]]
            ans.append(item)
    else:
        vegan_ingredients = [
            ing["name"] for ing in database["ingredients"] if "vegan" in ing["groups"]
        ]
        for meal in database["meals"]:
            is_vegan_meal = True
            for ing in meal["ingredients"]:
                if ing["name"] not in vegan_ingredients:
                    is_vegan_meal = False
                    break
            if not is_vegan_meal:
                continue

            item = {}
            item["id"] = meal["id"]
            item["name"] = meal["name"]
            item["ingredients"] = [ing["name"] for ing in meal["ingredients"]]
            ans.append(item)

    return responseFormatter(ans)


def getMealHandler(requestData):
    """
    Handling get meal request with its id requests
    """
    if requestData["params"] == "":
        raise RequiredParametersNotAvialble(
            "Parameter called id is required for this operation"
        )
    try:
        id = int(requestData["params"]["id"])
    except:
        raise InvalidParameterValue("The passed id value is invalid")

    item = getMeal(database, id)
    ingList = []
    for itemIng in item["ingredients"]:
        for ing in database["ingredients"]:
            if ing["name"] == itemIng["name"]:
                ingList.append(ing)
                break
    item["ingredients"] = ingList
    return responseFormatter(item)


def qualityCaculationHandler(requestData):
    """
    This function calculates the quality of a meal
    """
    if requestData["body"] == "" or "meal_id" not in requestData["body"]:
        raise RequiredParametersNotAvialble("meal_id is required for this operation")

    id = int(requestData["body"]["meal_id"])
    meal = getMeal(database=database, id=id)
    quality = qualityCalculator(meal, requestData["body"])
    ans = {"quality": quality}
    body = json.dumps(ans, indent=2) + "\n"
    result = (len(body), body)
    return result


def priceCaculationHandler(requestData):
    """
    This function calculates the price of a meal
    """
    if requestData["body"] == "" or "meal_id" not in requestData["body"]:
        raise RequiredParametersNotAvialble("meal_id is required for this operation")

    id = int(requestData["body"]["meal_id"])
    meal = getMeal(database, id)
    price = priceCalulator(database, meal, requestData["body"])
    ans = {"price": price}
    return responseFormatter(ans)




def getRandomOptionsWithinBudget(budget, meal):
    currentCost = calculateMinOfMeal(database=database, meal=meal)
    options = {}
    for ing in meal["ingredients"]:
        costs = calculateCostsOfIngredient(ing, database)
        min_ing_cost = calculateIngredientMinCost(ing, database)
        new_config = random.choice(costs)
        if (currentCost - min_ing_cost[0] + new_config[0]) < budget:
            options[ing["name"].lower()] = new_config[1]
            currentCost = currentCost - min_ing_cost[0] + new_config[0]
        else:
            options[ing["name"].lower()] = min_ing_cost[1]
    return options


def randomHandler(data):
    ans = {}
    if data["body"] == "":
        is_finished = False
        while not is_finished:
            try:
                meal = random.choice(database["meals"])
                options = {}
                ingredientsQuality = []
                for ing in meal["ingredients"]:
                    ingQuality = random.choice(["high", "low", "medium"])
                    options[ing["name"].lower()] = ingQuality
                    ingredientsQuality.append(
                        {"name": ing["name"], "quality": ingQuality}
                    )

                price = priceCalulator(database, meal, options)
                ans["id"] = meal["id"]
                ans["name"] = meal["name"]
                ans["price"] = price
                ans["quality_score"] = qualityCalculator(meal, options)
                ans["ingredients"] = ingredientsQuality
            except:
                continue
            is_finished = True
    else:
        budget = float(data["body"]["budget"])
        allowedMeals = allowedInBudgetMealsIds(budget, database)
        meal_id = random.choice(allowedMeals)
        meal = getMeal(meal_id)
        options = getRandomOptionsWithinBudget(budget, meal)
        price = priceCalulator(database, meal, options)
        ans["id"] = meal["id"]
        ans["name"] = meal["name"]
        ans["price"] = price
        ans["quality_score"] = qualityCalculator(meal, options)

        ans["ingredients"] = [{"name": op, "quality": options[op]} for op in options]

    body = json.dumps(ans, indent=2) + "\n"
    result = (len(body), body)
    return result


def searchHandler(data):
    if data["params"] == "":
        raise Exception()
    ans = []
    if "query" in data["params"]:
        search_term = data["params"]["query"].lower()
        for meal in database["meals"]:
            if search_term in meal["name"].lower():
                search_result = {
                    "id": meal["id"],
                    "name": meal["name"],
                    "ingredients": [ing["name"] for ing in meal["ingredients"]],
                }
                ans.append(search_result)

        body = json.dumps(ans, indent=2) + "\n"
        result = (len(body), body)
        return result
    else:
        raise Exception


def calculateIngredientNewUpgrade(meal, currentUpgrade):
    if currentUpgrade[1] == "high":
        raise Exception()

    mealIng = [ing for ing in meal["ingredients"] if currentUpgrade[0] == ing["name"]][
        0
    ]
    costsOfIng = getCostsOfIngredient(database=database, ing=mealIng)
    newQuality = currentUpgrade[1]
    newCost = currentUpgrade[2]
    if currentUpgrade[1] == "medium":
        newQuality = "high"
        newCost = math.inf
    elif currentUpgrade[1] == "low":
        newQuality = "medium"
        newCost = costsOfIng[0][0] - costsOfIng[1][0]
    else:
        newQuality = "low"
        newCost = costsOfIng[2][0]

    return (currentUpgrade[0], newQuality, newCost)


def calculateUpgradesCosts(meal, options):
    upgradesCosts = []
    for ing in meal["ingredients"]:
        option = ""
        if options[ing["name"].lower()] == "medium":
            option = "low"
        elif options[ing["name"].lower()] == "high":
            option = "medium"

        upgradesCosts.append(
            calculateIngredientNewUpgrade(meal, (ing["name"], option, 0))
        )
    return upgradesCosts


def findHighestQualityWithinBudget(meal, budget):
    """
    This function finds the highest quality of a meal within a specific budget and returns a tuple (quality, options)
    """
    currentCost, options = getMinCostAndOptionsOfMeal(database=database, meal=meal)
    currentQuality = qualityCalculator(meal=meal, body=options)
    numOfIngredients = len(meal["ingredients"])
    qualityIncreaseAmount = 10 / numOfIngredients
    # [("Ingredient Name", "current quality", <Upgrade cost>)]
    upgradesCosts = calculateUpgradesCosts(meal, options)
    while True:
        print(qualityIncreaseAmount, currentCost, currentQuality, upgradesCosts)
        print("******************************************")
        minUpgrade = 0
        for num in range(numOfIngredients):
            if (
                upgradesCosts[num][1] != "high"
                and upgradesCosts[num][2] < upgradesCosts[minUpgrade][2]
            ):
                minUpgrade = num

        tempCost = currentCost + upgradesCosts[minUpgrade][2]
        if tempCost < budget:
            currentCost = tempCost
            upgradesCosts[minUpgrade] = calculateIngredientNewUpgrade(
                meal, upgradesCosts[minUpgrade]
            )
            currentQuality += qualityIncreaseAmount
        else:
            break

    options = [(up[0], up[1]) for up in upgradesCosts]
    print("######################################################\n\n\n")
    return (currentCost, currentQuality, options)


def findHighestHandler(data):
    if data["body"] == "":
        raise Exception()
    if "budget" not in data["body"]:
        raise Exception()

    budget = float(data["body"]["budget"])
    allowedMealsIds = allowedInBudgetMealsIds(budget, database)
    quality = 0
    meal = None
    options = None
    price = 0
    for meal_id in allowedMealsIds:
        meal_temp = getMeal(meal_id)
        cost_temp, quality_temp, options_temp = findHighestQualityWithinBudget(
            meal_temp, budget
        )
        if quality_temp > quality:
            meal = meal_temp
            options = options_temp
            quality = quality_temp
            price = cost_temp

    ans = {}
    ans["id"] = meal["id"]
    ans["name"] = meal["name"]
    ans["price"] = price
    ans["quality_score"] = quality
    ans["ingredients"] = [{"name": op[0], "quality": op[1]} for op in options]
    return responseFormatter(ans)


def findHighestOfMealHandler(data):
    pass


# Avilable url patterns
urlpatterns = {
    "/listMeals": listMealsHandler,
    "/getMeal": getMealHandler,
    "/quality": qualityCaculationHandler,
    "/price": priceCaculationHandler,
    "/random": randomHandler,
    "/search": searchHandler,
    "/findHighest": findHighestHandler,
    "/findHighestOfMeal": findHighestOfMealHandler,
}

# parsing the requsts and returning the important data in a dictionary
def request_parser(request):
    result = {
        "type": "",
        "path": "",
        "params": "",
        "body": "",
    }

    headers = request.split("\n\r\n")[0].split("\n")
    result["type"] = headers[0].split()[0]
    # Parsing path and parameters
    try:
        path_params = headers[0].split()[1].split("?")
        result["path"] = path_params[0]
        params = path_params[1].split("&")
        params_dic = {}
        for param in params:
            param_lst = param.split("=")
            params_dic[param_lst[0].lower()] = param_lst[1]
        result["params"] = params_dic
    except:
        result["path"] = headers[0].split()[1]

    # Parsing the body
    try:
        body = request.split("\n\r\n")[1].split("&")
        body_dic = {}
        for i in body:
            item = i.split("=")
            body_dic[item[0].lower()] = item[1]
        result["body"] = body_dic
    except:
        result["body"] = ""

    return result


# Testing code

while True:
    # Wait for requests and parsing them
    c_connection, c_address = server.accept()
    request = c_connection.recv(1024).decode()
    print(request)
    request_data = request_parser(request)

    # Constructing the response
    try:
        response_content = urlpatterns[request_data["path"]](request_data)
        response = (
            f"HTTP/1.1 200 OK\nContent-Type: application/json\nContent-Length: {response_content[0]}\n\n"
            + response_content[1]
        )

    except RequiredParametersNotAvialble as e:
        response = f"HTTP/1.1 404 NOT FOUND\n\n{e.message}\n"
    except:
        response = "HTTP/1.1 404 NOT FOUND\n\nFile Not Found\n"

    c_connection.sendall(response.encode())
    c_connection.close()
    print("***************************************************************")
