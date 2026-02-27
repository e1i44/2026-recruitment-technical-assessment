from dataclasses import dataclass
from typing import List, Dict, Union
from flask import Flask, request, jsonify
import re

# ==== Type Definitions, feel free to add or modify ===========================
@dataclass
class CookbookEntry:
	name: str

@dataclass
class RequiredItem():
	name: str
	quantity: int

@dataclass
class Recipe(CookbookEntry):
	required_items: List[RequiredItem]

@dataclass
class Ingredient(CookbookEntry):
	cook_time: int

# =============================================================================
# ==== HTTP Endpoint Stubs ====================================================
# =============================================================================
app = Flask(__name__)

# Store your recipes here!
cookbook: list[CookbookEntry] = []

# Task 1 helper (don't touch)
@app.route("/parse", methods=['POST'])
def parse():
	data = request.get_json()
	recipe_name = data.get('input', '')
	parsed_name = parse_handwriting(recipe_name)
	if parsed_name is None:
		return 'Invalid recipe name', 400
	return jsonify({'msg': parsed_name}), 200

# [TASK 1] ====================================================================
# Takes in a recipeName and returns it in a form that 
def parse_handwriting(recipeName: str) -> Union[str | None]:
	spaced = recipeName.replace('_', ' ').replace('-', ' ')
	stripped = re.sub('[^a-zA-Z ]', '', spaced)

	allWords = stripped.rsplit()
	allWords = [i.capitalize() for i in allWords]

	result = ' '.join(allWords)

	if len(result) == 0:
		return None

	return result

# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()

	name = data.get('name', '')
	if search_cookbook(name) is not None:
		return f'Cookbook already has an entry with name {name}', 400

	type = data.get('type', '')
	result: Union[CookbookEntry | str]
	if type == 'recipe':
		itemsdata = data.get('requiredItems', '')
		result = create_recipe(name, itemsdata)
	elif type == 'ingredient':
		cooktime = data.get('cookTime', '')
		result = create_ingredient(name, cooktime)
	else:
		return 'Type must be recipe or ingredient', 400
	
	if isinstance(result, CookbookEntry):
		cookbook.append(result)
	else:
		return result, 400

	return '', 200


# returns an Ingredient item or a string error
def create_ingredient(name: str, cooktime: str):
	cooktimeval = getInt(cooktime)
	if cooktimeval < 0:
		return 'Cooktime must be an integer greater than or equal to 0'
	
	return Ingredient(name, cooktimeval)


# returns a Recipe item or a string error
def create_recipe(name: str, itemsdata):
	itemslisted = [RequiredItem(i.get('name', ''), i.get('quantity', '')) for i in itemsdata]
	items = []

	for i in itemslisted:
		if i.name == '' or i.quantity == '':
			return 'Recipe requiredItems missing name or quanitity'

		duplicates = [j for j in itemslisted if j.name == i.name]
		if len(duplicates) > 1: 
			return 'Recipe requiredItems can only have one element per name'
		
		quantity = getInt(i.quantity)
		if quantity < 1:
			return 'Quantity must be an integer greater than or equal to 1'

		items.append(RequiredItem(i.name, quantity))

	return Recipe(name, items)


# returns the int conversion of a string or -1 on error
def getInt(input: str):
	try:
		return int(input)
	except:
		return -1


# returns a cookbook item with a given name or None if it doesnt exist
def search_cookbook(name: str) -> Union[CookbookEntry | None]:
	items = [i for i in cookbook if i.name == name]
	
	if len(items) == 0:
		return None

	return items[0]


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	name = request.args.get('name')
	if search_cookbook(name) is None:
		return 'Recipe with name not found', 400
	if isinstance(search_cookbook(name), Ingredient):
		return 'Can only summarise recipes, not ingredients', 400
	
	try:
		cooktime = getCookTimeByName(name)
	except Exception as e:
		return f'Failed to summarise recipe due to issue with required items: {e}', 400

	baseingredients = getBaseIngredients(name, 1)

	return jsonify({
		'name': name,
		'cookTime': cooktime,
		'ingredients': baseingredients
	})


def getCookTimeByName(name: str) -> int:
	item: Union[ CookbookEntry | None ] = search_cookbook(name)

	if isinstance(item, Recipe):
		cooktime = 0
		for i in item.required_items:
			cooktime += getCookTimeByName(i.name) * i.quantity
		return cooktime

	elif isinstance(item, Ingredient):
		return item.cook_time
	
	else:
		raise Exception(f'{name} not found in cookbook') 


def getBaseIngredients(name: str, quantity: int) -> List[RequiredItem]:
	item: CookbookEntry = search_cookbook(name)
	if isinstance(item, Recipe):
		ingredients = []
		addIngredients(ingredients, item.required_items, quantity)
		return ingredients
	else:
		return [RequiredItem(name, quantity)]


def addIngredients(ingredients: List[RequiredItem], new_ingredients: List[RequiredItem], multiplier: int):
	for i in new_ingredients:
		existingingredient = [j for j in ingredients if j.name == i.name]
		if len(existingingredient) > 0:
			existingingredient[0].quantity += i.quantity * multiplier
			return

		item = search_cookbook(i.name)

		if isinstance(item, Recipe):
			addIngredients(ingredients, getBaseIngredients(i.name, i.quantity * multiplier), 1)
		else:
			ingredients.append(RequiredItem(i.name, i.quantity * multiplier))


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
