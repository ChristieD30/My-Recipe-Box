from app.model.recipes import Recipe
from app import db

class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, instructions, user_id=None):
        try:
            # Check if recipe with the same name exists for this user
            existing = Recipe.query.filter_by(name=name, user_id=user_id).first()
            if existing:
                return None, "Recipe name already exists. Please rename it."

            new_recipe = Recipe(name=name, ingredients=ingredients, user_id=user_id)
            new_recipe = Recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                user_id=user_id
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
