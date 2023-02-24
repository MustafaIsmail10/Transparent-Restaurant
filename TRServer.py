import socket, sys, json
from exceptions import *

# Getting and parsing the data base
file_path = "data.json"
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


def listMealsHandler(data):
    options = data["params"]

    is_vegan = False
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

    body = json.dumps(ans, indent=2) + "\n"
    result = (len(body), body)
    return result


def getMeal(id):
    item = [meal for meal in database["meals"] if meal["id"] == id]
    if item == []:
        raise RequiredParametersNotAvialble(
            "The Passed id invalid. Please pass an id with a proper id"
        )
    return item[0]


def getMealHandler(data):
    if data["params"] == "":
        raise RequiredParametersNotAvialble(
            "Parameter called id is required for this operation"
        )

    id = int(data["params"]["id"])
    item = getMeal(id)

    ingList = []
    for itemIng in item["ingredients"]:
        for ing in database["ingredients"]:
            if ing["name"] == itemIng["name"]:
                ingList.append(ing)
                break
    item["ingredients"] = ingList

    body = json.dumps(item, indent=2) + "\n"
    result = (len(body), body)
    return result


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


def qualityCaculationHandler(data):
    if data["body"] == "":
        raise RequiredParametersNotAvialble("Id is required for this operation")

    id = int(data["body"]["meal_id"])
    meal = getMeal(id)
    quality = qualityCalculator(meal, data["body"])
    ans = {"quality": quality}
    body = json.dumps(ans, indent=2) + "\n"
    result = (len(body), body)
    return result


def priceCalulator(meal, body):
    total_price = 0
    for ing in meal["ingredients"]:
        ingOptions = [
            ingOption
            for ingOption in database["ingredients"]
            if ing["name"] == ingOption["name"]
        ][0]["options"]

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


def priceCaculationHandler(data):
    if data["body"] == "":
        raise RequiredParametersNotAvialble("Id is required for this operation")

    id = int(data["body"]["meal_id"])
    meal = getMeal(id)
    price = priceCalulator(meal, data["body"])
    ans = {"price": price}
    body = json.dumps(ans, indent=2) + "\n"
    result = (len(body), body)
    return result


# Avilable url patterns
urlpatterns = {
    "/listMeals": listMealsHandler,
    "/getMeal": getMealHandler,
    "/quality": qualityCaculationHandler,
    "/price": priceCaculationHandler,
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
            params_dic[param_lst[0]] = param_lst[1]
        result["params"] = params_dic
    except:
        result["path"] = headers[0].split()[1]

    # Parsing the body
    try:
        body = request.split("\n\r\n")[1].split("&")
        body_dic = {}
        for i in body:
            item = i.split("=")
            body_dic[item[0]] = item[1]
        result["body"] = body_dic
    except:
        result["body"] = ""

    return result


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

# Close socket
server_socket.close()


#############################################################################

# from http.server import *
# class RequestHandler(BaseHTTPRequestHandler):
#     def do_GET(self):
#         self.send_response(200)
#         self.send_header('content-type', 'text/html')
#         self.end_headers()
#         output = ""
#         output += "<html><body>"
#         output += "<h1> Text Analyzer </h1>"

#         output += '<form method="POST" enctype="multipart/form-data" action="/analyze/result">'
#         output += '<label for="fname">Text: </label>'
#         output += '<input name="task" type="text" placeholder="Enter text" size="100">'
#         output += '</br>'
#         output += '<input type="submit" value="Analyze">'
#         output += '</form>'
#         output += "</body></html>"
#         self.wfile.write(output.encode())


# def run(server_class=HTTPServer, handler_class=RequestHandler):
#     server_address = ("", 8000)
#     httpd = server_class(server_address, handler_class)
#     httpd.serve_forever()


# run(HTTPServer, RequestHandler)
