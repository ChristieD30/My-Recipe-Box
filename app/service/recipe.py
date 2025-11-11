from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.model.recipes import Recipe
from app.enums import Category
from app import db


class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, instructions, category, user_id=None, prep_time=None, cook_time=None, total_time=None, servings=None):
        try:
            # Check if the recipe already exists for the user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please rename it."
            
            # Validate the category
            if category not in [cat.value for cat in Category]:
                return None, f"Invalid category. Valid categories are: {[cat.value for cat in Category]}"

            # Create new recipe object
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category=category,
                user_id=user_id,  # can't leave this null
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings,
            )
            
            db.session.add(new_recipe)
            db.session.commit()  # Commit the recipe first to get the ID

            message = f"Your recipe '{name}' is added."
            return new_recipe, message
        except Exception as e:
            db.session.rollback()
            print(f"Error adding recipe: {str(e)}")
            raise

    @staticmethod
    def delete_recipe(recipe_id, user_id=None):
        print("Recipe deletion must be requested by emailing myrecipieboxsupport@example.com.")
        return {
            "error": "Recipe deletion is not available through this interface. "
                     "Please email myrecipieboxsupport@example.com to request recipe deletion."
        }

    @staticmethod
    def update_recipe_as_duplicate(_id, _name=None, _ingredients=None, _instructions=None, user_id=None, prep_time=None, cook_time=None, total_time=None, servings=None):
        try:
            # Fetch the original recipe to duplicate
            original = Recipe.query.filter_by(id=_id).first()
            if not original:
                return None, "Unable to duplicate recipe."

            # Set values for the new recipe
            name = _name or original.name + " (Copy)"
            ingredients = _ingredients or original.ingredients
            instructions = _instructions or original.instructions

            # Check if the recipe with this name already exists for the user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please choose a different name."

            # Create the new duplicated recipe
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                user_id=user_id,
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings
            )

            db.session.add(new_recipe)
            db.session.commit()  # Commit the new recipe first to get the ID

            message = f"Your updated recipe '{name}' has been created as a duplicate."
            return new_recipe, message

        except Exception as e:
            db.session.rollback()
            print(f"Error duplicating recipe: {str(e)}")
            raise

    @staticmethod
    def search_recipes(query=None, category=None):
        """Modern search: searches across ingredients, category, and recipe name."""
        recipes_query = Recipe.query
        if query:
            search_term = f"%{query.lower()}%"
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.ingredients.ilike(search_term),
                    Recipe.category.ilike(search_term),
                    Recipe.name.ilike(search_term)
                )
            )
        if category:
            recipes_query = recipes_query.filter(Recipe.category.ilike(f"%{category}%"))
        return recipes_query.all()

    @staticmethod
    def get_random_recipe(exclude_ids=None):
        """Fetch one random recipe from the database."""
        query = Recipe.query
        if exclude_ids:
            query = query.filter(~Recipe.id.in_(exclude_ids))
        recipe = query.order_by(db.func.random()).first()
        if recipe:
            return recipe, "Hello there! Your random kitchen adventure awaits. Try it before it vanishes!\n"
        else:
            return None, "No recipes found."
