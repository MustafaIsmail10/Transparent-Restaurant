# Transparent Restaurant Backend

This is my implementation for the Transparent Restaurant Backend project 

## Running

* Change directory to the directory of the project

* Add the database with the name "data.json" in the same directory as the project

* You can pass the path to the database as a parameter to the project 

* Run TRServer.py 

```shell
python3 TRServer.py #<optional> path to the database
```

## Implementation Details

### Sockek

I imported socket library in python and programmed the socket to listen to port 8080.

### Request Parser

I have manully parsed HTTP request that comes to port 8080 and extraced all the data that i need from the request. The implementation is request_parser function in TRServer.py

In the request_parser function, I extract the information from http request text and construct a dictionary to hold this data for further processing 

### Routing

I'm using a dictionary that is called urlpatterns to call the correct handler that can response to the comming request.

### listMealsHandler(requestData)

This function respond to /listMeals request by 

* making some error checking 

* checking the optional flags such as is_vegan and is_vegeterian

* based on the flags it either 
  
  * list all meals in database if there is no flags
  
  * list vegeterian meals if is_vegeterian is passed as true
  
  * list vegan meals if is_vegan flag is passed as true

* It then calls responseFormatter function that converts the resulting dictionary to JSON format

### getMealHandler(requestData)

This function respond to /getMeal request by

* making some error checking

* Calling the function getMeal that take meal_id and goes over the data base to find that meal 

* if the meal is not in database send an error

* if the meal in database send it back in json format

### qualityCaculationHandler(requestData)

This function respond to /quality request by

* making some error checking 

* get the meal indicated by meal_id

* calculate the quality by calling the function qualityCalculator which do the following
  
  * go over the ingredient of the meal and check their quality in the passed arguments or use default value and based on that detects their quality value 
  
  * adds all the qualities of ingrediets and get their avergare to be the quality of the meal

* returns the result in JSON format



### priceCaculationHandler(requestData)

This function respond to /quality request by

- making some error checking

- get the meal indicated by meal_id

- calculate the quality by calling the function priceCalulator which do the following
  
  - go over the ingredient of the meal and get their options from the database
  
  - Based on whether the ingrdient quality is passed or not it eather 
    
    - calculate the cost of an ingredient the according to the passed quality by multiplying the quantity used in the meal by the value of the passd quality
    
    - calculate the cost of an ingredient the according to the default quality by multiplying the quantity used in the meal by the value of the default quality
  
  - Adds the value of all ingredients and returns the total value

- returns the price in JSON format



### randomHandler(requestData)

This function responde to /random post requests by 

* makihg some error checking 

* depending on whether budget parameter is correctly provided it may either 
  
  * If the budget parameter is not provided, it will
    
    * get a random meal  
    
    * choose a random option for each ingredient inside the meal 
    
    * calculate the price and quantity of the chosen meal and chosen options
  
  * if the budget parameter is provided, it will
    
    * calculate the meals that has minimum cost below the budget if no meal exist it will raise an error
    
    * minimum cost meals below budget is calculated by 
      
      * calculate the minimum price of all meals and choosing the meals with price below budget
      
      * calculating minimum price of a meal is done by calculating the minumu price for each ingredient 
      
      * the minimum price for each ingredient is calculated by comparing various prices of the ingredient (low, medium, high) for the meal with respect to the chosen quantity and cost incured by degrading the quality. 
      
      * After getting minimum cost of all meal, the meals with minium cost below budget is chosen 
    
    * We select a random meal from the list of allowed meals 
    
    * We compute random comfigrations for the chosen meal by 
      
      * going over all the ingredient of the meal getting a random configratoin for each taking into consideration whether this new configuration will raise the cost of the meal above the budget
      
      * if a chosen ingredient quality goes above budget the minimum cost configuration is chosen
    
    * After getting random meal with random configuration below budget the quality of the meal is calculated 

* The meal data is put into appropriate format and converted to JSON to be send as a response



### searchHandler(requestData)

This function responde to /search GET requests by

* Making some error checking 

* go over all meals in database and chose meals that has the seach term in their name

* return list of those meals in JSON format



### findHighestHandler(requestData)

This function responde to /findHighest PIST requests by

* Making some error checking 

* 
