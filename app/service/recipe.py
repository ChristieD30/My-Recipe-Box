from datetime import datetime
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy

from app.model.recipes import Recipe
from app.enums import Category
from app import db

class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, instructions, category, user_id=None):
        try:
            # Check if recipe with the same name exists for this user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please rename it."
            
            if category not in [cat.value for cat in Category]:
                return None, f"Invalid category. Valid categories are: {[cat.value for cat in Category]}"

            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category=category,
                user_id=user_id # can't leave this null
            )
            db.session.add(new_recipe)
            db.session.commit()
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
    def update_recipe_as_duplicate(_id, _name=None, _ingredients=None, _instructions=None, _category=None, user_id=None, user_name=None):
        try:
            # Fetch the original recipe
            original = Recipe.query.filter_by(id=_id).first()
            if not original:
                return None, "Unable to duplicate recipe."

            # Use original data from orginal recipe
            name = (_name or original.name) + " (" + user_name + " Copy)"
            ingredients = _ingredients or original.ingredients
            instructions = _instructions or original.instructions
            category = _category or original.category

            # Check if the duplicated recipe name already exists for this user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please choose a different name."

            # Create new duplicated recipe owned by the user duplicating it
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category= category,
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
    def owner_update_recipe(recipe_id, name=None, ingredients=None, instructions=None, category=None, user_id=None):
        try:
            # Ensure the recipe exists and is owned by the provided user_id
            recipe = Recipe.query.filter_by(id=recipe_id, user_id=user_id).first()
            if not recipe:
                return None, "Recipe not found or you do not have permission to update it."
            # Update fields when provided
            if name:
                # Check for name uniqueness for this user
                existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
                if existing and existing.id != recipe_id:
                    return None, "Recipe name already exists. Please choose a different name."
                recipe.name = name

            if ingredients:
                recipe.ingredients = ingredients

            if instructions:
                recipe.instructions = instructions

            if category:
                if category not in [cat.value for cat in Category]:
                    return None, f"Invalid category. Valid categories are: {[cat.value for cat in Category]}"
                recipe.category = category

            recipe.updated_at = datetime.utcnow()
            db.session.commit()
            message = f"Your recipe '{recipe.name}' has been updated."
            return recipe, message

        except Exception as e:
            db.session.rollback()
            print(f"Error updating recipe: {str(e)}")
            raise
    @staticmethod
    def search_recipes(query=None, category=None):
        """
        Modern search: searches across ingredients, category, and recipe name
        """
        recipes_query = Recipe.query
        
        if query:
            # Search across multiple fields
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
    def get_random_recipe():
        recipe = Recipe.query.order_by(db.func.random()).first()
        if recipe:
            return recipe, f"Hello there! Your random kitchen adventure awaits. Try it before it vanishes!\n"
        else:
            return None, "No recipes found."

