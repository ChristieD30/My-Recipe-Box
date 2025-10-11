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

    @staticmethod
    def get_recipes_by_ingredients(ingredients):
        try:
            print(f"ingredients: {ingredients}")
            if not ingredients or not ingredients.strip():
                # If no search terms, return empty list (or all recipes if you prefer)
                return []
            # Split search terms by comma, strip whitespace, and lower
            search_terms = [term.strip().lower() for term in ingredients.split(',') if term.strip()]
            if not search_terms:
                return []
            recipes = Recipe.query.all()
            print(f"Search terms: {search_terms}")
            filtered = []
            for recipe in recipes:
                # Split recipe ingredients into lines, strip and lower each
                recipe_ingredient_lines = [line.strip().lower() for line in recipe.ingredients.split('\n') if line.strip()]
                # For each search term, check if it is a substring of any ingredient line
                if all(any(term in ingredient_line for ingredient_line in recipe_ingredient_lines) for term in search_terms):
                    filtered.append(recipe)
            print(f"Filtered recipes: {[r.name for r in filtered]}")
            return filtered
        except Exception as e:
            print(f"Error retrieving recipes: {str(e)}")
            raise
 