import os
import sys
from datetime import datetime

# Set up path - go up two levels to reach the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app import db, create_app
from app.service.recipe import RecipeService
from app.model.recipes import Recipe

#print("Import successful!")

# Setup Flask app context and in-memory database for testing
app = create_app()
app.app_context().push()

db.create_all()

# will probably want to filter by user_id once we start adding users
# will also need to add user_id argument at that time
def read_recipes():
#def read_recipes(uid):
    recs = Recipe.query.all()
    #recs = Recipe.query.filterby(user_id=uid)
    for r in recs:
        print("Name:\n",r.name)
        print()
        print("Ingredients:\n", r.ingredients)
        print()
        print("Instructions:\n", r.instructions)
        print()
        print("Created At:\n", r.created_at)
        print()
        print("Updated At:\n", r.updated_at)
        print()

def update_recipe(_id, _name, _ingredients, _instructions):
    # this procedure is untested because I can't get data back in the database
    rec = Recipe.query.filter_by(id=_id).first()
    #sqlalchemy supposedly allows direct access to record attributes
    rec.name = _name
    rec.ingredients = _ingredients
    rec.instructions = _instructions
    rec.updated_at = datetime.now()
    db.session.commit()


if __name__ == "__main__":
    try:
        update_recipe(15, "new name", "new ingredients", "new instructions")
        read_recipes()
    except Exception as e:
        print(f"Error occurred: {e}")