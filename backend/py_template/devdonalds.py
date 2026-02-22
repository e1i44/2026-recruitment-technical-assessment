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
	# TODO: implement me
	return recipeName


# [TASK 2] ====================================================================
# Endpoint that adds a CookbookEntry to your magical cookbook
@app.route('/entry', methods=['POST'])
def create_entry():
	data = request.get_json()

	name = data.get('name', '')
	if search_cookbook(name) is not None:
		return f'Cookbook already has an entry with name {name}', 400

	type = data.get('type', '')
	result: CookbookEntry | str
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
def search_cookbook(name: str):
	items = [i for i in cookbook if i.name == name]
	
	if len(items) == 0:
		return None

	return items[0]


# [TASK 3] ====================================================================
# Endpoint that returns a summary of a recipe that corresponds to a query name
@app.route('/summary', methods=['GET'])
def summary():
	# TODO: implement me
	return 'not implemented', 500


# =============================================================================
# ==== DO NOT TOUCH ===========================================================
# =============================================================================

if __name__ == '__main__':
	app.run(debug=True, port=8080)
