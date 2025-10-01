
from app.model.recipes import Recipe
from app import db

class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, user_id=1):
        try:
            new_recipe = Recipe(name=name, ingredients=ingredients, user_id=user_id)
            db.session.add(new_recipe)
            db.session.commit()
            return new_recipe
        except Exception as e:
            db.session.rollback()
            print(f"Error adding recipe: {str(e)}")
            raise
