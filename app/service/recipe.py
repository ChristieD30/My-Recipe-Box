from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from app import db
from app.model.recipes import Recipe

class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, instructions=''):
        recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions)
        db.session.add(recipe)
        db.session.commit()
        return recipe

    @staticmethod
    def get_random_recipe():
        recipe = Recipe.query.order_by(db.func.random()).first()
        if recipe:
            return recipe, f"Hello there! Your random kitchen adventure awaits. Try it before it vanishes!\n"
        else:
            return None, "No recipes found."
    @staticmethod
    def delete_recipe(recipe_id, user_id=None):
        print("Recipe deletion must be requested by emailing myrecipieboxsupport@example.com.")
        return {
            "error": "Recipe deletion is not available through this interface. "
                     "Please email myrecipieboxsupport@example.com to request recipe deletion."
        }
    
    @staticmethod
    def update_recipe_as_duplicate(_id, _name=None, _ingredients=None, _instructions=None, user_id=None):
        try:
            # Fetch the original recipe
            original = Recipe.query.filter_by(id=_id).first()
            if not original:
                return None, "Unable to duplicate recipe."

            # Use original data from orginal recipe
            name = _name or original.name + " (Copy)"
            ingredients = _ingredients or original.ingredients
            instructions = _instructions or original.instructions

            # Check if the duplicated recipe name already exists for this user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please choose a different name."

            # Create new duplicated recipe owned by the user duplicating it
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                user_id=user_id
            )

            db.session.add(new_recipe)
            db.session.commit()

            message = f"Your updated recipe '{name}' has been created as a duplicate."
            return new_recipe, message

        except Exception as e:
            db.session.rollback()
            print(f"Error duplicating recipe: {str(e)}")
            raise

    @staticmethod
    def search_recipes(ingredients=None, category=None):
        try:
            print(f"ingredients: {ingredients}, category: {category}")
            query = Recipe.query
            # Filter by category if provided
            if category and category.strip():
                query = query.filter(Recipe.category.ilike(f"%{category.strip()}%"))
            # Filter by ingredients if provided
            if ingredients and ingredients.strip():
                search_terms = [term.strip().lower() for term in ingredients.split(',') if term.strip()]
                if search_terms:
                    recipes = query.all()
                    filtered = []
                    for recipe in recipes:
                        recipe_ingredient_lines = [line.strip().lower() for line in recipe.ingredients.split('\n') if line.strip()]
                        if all(any(term in ingredient_line for ingredient_line in recipe_ingredient_lines) for term in search_terms):
                            filtered.append(recipe)
                    print(f"Filtered recipes: {[r.name for r in filtered]}")
                    return filtered
                else:
                    return query.all()
            else:
                # If no ingredients filter, just return by category (or all)
                return query.all()
        except Exception as e:
            print(f"Error retrieving recipes: {str(e)}")
            raise

