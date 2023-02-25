# Transparent Restaurant Backend

This is my implementation for the Transparent Restaurant Backend project

## Running

- Change the directory to the directory of the project
- Add the database with the name "data.json" in the same directory as the project
- You can pass the path to the database as a parameter to the project
- Run TRServer.py

```shell
python3 TRServer.py #<optional> path to the database
```

## Implementation Details

### Socket

I imported the socket library in python and programmed the socket to listen to port 8080.

### Request Parser

I have manually parsed the HTTP request that comes to port 8080 and extracted all the data that I need from the request. The implementation is the request_parser function in TRServer.py

In the request_parser function, I extract the information from the HTTP request text and construct a dictionary to hold this data for further processing

### Routing

I'm using a dictionary that is called urlpatterns to call the correct handler that can respond to the coming request.

### listMealsHandler(requestData)

This function responds to /listMeals requests by

- making some error checking

- checking the optional flags such as is_vegan and is_vegeterian

- based on the flags it either
  
  - list all meals in the database if there are no flags
  
  - list vegetarian meals if is_vegeterian is passed as true
  
  - list vegan meals if the is_vegan flag is passed as true

- It then calls the responseFormatter function that converts the resulting dictionary to JSON format

### getMealHandler(requestData)

This function responds to /getMeal requests by

- making some error checking
- Calling the function getMeal that takes meal_id and goes over the database to find that meal
- if the meal is not in the database send an error
- if the meal is in the database send it back in JSON format

### qualityCaculationHandler(requestData)

This function responds to /quality requests by

- making some error checking

- get the meal indicated by meal_id

- calculate the quality by calling the function qualityCalculator which does the following
  
  - go over the ingredient of the meal and check their quality in the passed arguments or use the default value and based on that detects their quality value
  
  - adds all the qualities of ingredients and gets their average to be the quality of the meal

- returns the result in JSON format

### priceCaculationHandler(requestData)

This function responds to /quality requests by

- making some error checking

- get the meal indicated by meal_id

- calculate the quality by calling the function priceCalulator which does the following
  
  - go over the ingredient of the meal and get their options from the database
  
  - Based on whether the ingredient quality is passed or not it either
  
  - calculate the cost of an ingredient the according to the passed quality by multiplying the quantity used in the meal by the value of the passed quality
  
  - calculate the cost of an ingredient the according to the default quality by multiplying the quantity used in the meal by the value of the default quality
  
  - Adds the value of all ingredients and returns the total value

- returns the price in JSON format

### randomHandler(requestData)

This function responds to /random post requests by

- making some error checking

- depending on whether the budget parameter is correctly provided it may either

- If the budget parameter is not provided, it will
  
  - get a random meal
  
  - choose a random option for each ingredient inside the meal
  
  - calculate the price and quantity of the chosen meal and chosen options

- if the budget parameter is provided, it will
  
  - calculate the meals that have a minimum cost below the budget if no meal exists it will raise an error
  
  - minimum cost meals below budget are calculated by
    
    - calculate the minimum price of all meals and choose the meals with prices below budget
    
    - calculating the minimum price of a meal is done by calculating the minimum price for each ingredient
    
    - the minimum price for each ingredient is calculated by comparing various prices of the ingredient (low, medium, high) for the meal with respect to the chosen quantity and cost incurred by degrading the quality.
  
  - After getting the minimum cost of all meal, the meals with a minimum cost below budget is chosen
  
  - We select a random meal from the list of allowed meals
  
  - We compute random configurations for the chosen meal by
    
    - going over all the ingredients of the meal getting a random configuration for each taking into consideration whether this new configuration will raise the cost of the meal above the budget
  
  - if a chosen ingredient quality goes above budget the minimum cost configuration is chosen
  
  - After getting a random meal with a random configuration below budget the quality of the meal is calculated

- The meal data is put into the appropriate format and converted to JSON to be sent as a response

### searchHandler(requestData)

This function responds to /search GET requests by

- Making some error checking
- go over all meals in the database and chose meals that have the search term in their name
- return the list of those meals in JSON format

### findHighestHandler(requestData)

This function responds to /finds the highest POST requests by

- Making some error checking
- get all meals that have a minimum cost below budget using the same way as in **randomHandler(requestData)**
- Go over the list of allowed meals and choose the meals that are vegan, vegetarian, or neither depending on the passed parameters, and modify the allowed list of meals
- go over the modified allowed list of meals and find the highest quality for each meal within budget using the algorithm that will be mentioned in **findHighestOfMealHandler(requestData)**
- Then choose the meal that has the highest quality and calculate its price
- Put the chosen meal in the appropriate format and send it back in JSON

### findHighestOfMealHandler(requestData)

This function responds to /findHighestMeal POST requests by

- Making some error checking

- get the required meal by meal_id

- checks if the minimum cost of the meal is below budget using the algorithm mentioned in **randomHandler(requestData)**

- if the minimum cost of the meal is below budget it calls findHighestQualityWithinBudget which finds the highest quality for that meal with a cost below budget by
  
  - getting the minimum cost configuration of the meal then following a greedy approach it keeps picking the quality upgrade with minimum cost until no more upgrades are available that would keep the cost below budget.
  
  - In more details
    
    - After getting the minimum cost configurations
    
    - The quality of the minimum cost configuration is calculated
    
    - upgrade cost of each ingredient is then computed by
    
    - subtracting the cost of the higher quality from the cost of the current quality
    
    - The ingredient with the minimum upgrade cost is upgraded if upgrading it will not make the cost of the meal go above budget its upgrade cost is updated
    
    - After no upgrades are available the function returns the cost, quality, and options of the meal with the highest quality

- After getting the configuration of the highest quality, the data is put in the appropriate format and sent back in JSON

## Conclusion

This was a very interesting project with several nice challenges. There is still room for improvement such as using oop in the design that may make the code more readable and understandable.
