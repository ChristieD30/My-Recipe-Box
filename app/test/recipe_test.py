import os
import sys
from sqlalchemy import delete

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app import db, create_app
from app.service.recipe import RecipeService
from app.model.recipes import Recipe

app = create_app()
app.app_context().push()

app.config['TESTING'] = True

db.create_all()


# Run tests 
if __name__ == "__main__":
    try:
        RecipeService.add_recipe("Test", "Ingredients", "Instructions", "Category", 1)
        RecipeService.read_recipes()
        rec = Recipe.query.filter_by(name="Test").first()
        RecipeService.update_recipe(rec.id, "New Name", "New Ingredients", "New Instructions", "New Category")
        RecipeService.read_recipes()

# need to delete test row
#        rec = Recipe.query.filter_by(name="Test").first()
#        db.session.delete(rec)
#        db.session.commit()

    except Exception as e:
        print(f"Error occurred: {e}")



        