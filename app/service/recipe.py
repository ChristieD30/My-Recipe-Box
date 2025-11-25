from datetime import datetime
from flask import Flask, request, jsonify, current_app
from flask_sqlalchemy import SQLAlchemy
from app.model.recipes import Recipe
from app.enums import Category
from werkzeug.utils import secure_filename
import os 
from app import db


class RecipeService:
    # File upload configuration
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @staticmethod
    def allowed_file(filename):
        """Check if file has allowed extension"""
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in RecipeService.ALLOWED_EXTENSIONS

    @staticmethod
    def save_recipe_image(file):
        """Save uploaded image and return the file path"""
        if file and RecipeService.allowed_file(file.filename):
            # Create uploads directory if it doesn't exist
            upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'recipes')
            os.makedirs(upload_folder, exist_ok=True)
            
            # Generate unique filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{timestamp}_{secure_filename(file.filename)}"
            
            # Save file
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            # Return just the filename for database storage
            # Template will construct full path
            return filename
        return None

    @staticmethod
    def add_recipe(name, ingredients, instructions, category, user_id=None, prep_time=None, cook_time=None, total_time=None, servings=None, image_location=None):
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
                image_location=image_location,
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings
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
    def update_recipe_as_duplicate(_id, _name=None, _ingredients=None, _instructions=None, user_id=None, prep_time=None, cook_time=None, total_time=None, servings=None, _category=None, user_full_name=None, _image_location=None):
        try:
            # Fetch original recipe
            original = Recipe.query.filter_by(id=_id).first()
            if not original:
                return None, "Unable to duplicate recipe."

            # Duplicate fields
            name = original.name
            category = _category or original.category
            ingredients = _ingredients or original.ingredients
            instructions = _instructions or original.instructions
            image_location = _image_location or original.image_location

            # Prevent duplicate name for same user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please choose a different name."

            # Create new duplicated recipe
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                user_id=user_id,
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings,
                image_location=image_location,
                category=category
            )

            db.session.add(new_recipe)
            db.session.commit()

            # IMPORTANT FIX: refresh so SQLAlchemy loads new_recipe.user
            db.session.refresh(new_recipe)

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

    @staticmethod
    def update_recipe(recipe_id, name=None, ingredients=None, instructions=None, category=None, user_id=None, image_location=None):
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
            
            if image_location:
                recipe.image_location = image_location

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
