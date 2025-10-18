import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from app import create_app, db
from app.service.recipe import RecipeService
from app.model.users import User

app = create_app()

with app.app_context():
    # Get users before fetching random recipe
    users_before = User.query.all()
    user_count_before = len(users_before)
    user_list_before = [f"{user.id}:{user.username}" for user in users_before]
    
    print(f"Users before get_random_recipe() ({user_count_before}): {user_list_before}")
    
    # Get random recipe
    recipe, message = RecipeService.get_random_recipe()
    
    # Get users after fetching random recipe
    users_after = User.query.all()
    user_count_after = len(users_after)
    user_list_after = [f"{user.id}:{user.username}" for user in users_after]
    
    print(f"Users after get_random_recipe() ({user_count_after}): {user_list_after}")
    
    # Print whether a new user was created
    if user_count_after > user_count_before:
        print(f"New user was created during get_random_recipe()!")
    else:
        print(f"No new user was created during get_random_recipe().")
    
    # Print the random recipe details
    if recipe:
        print(f"{message} Recipe: {recipe.name} - Ingredients: {recipe.ingredients} - Instructions: {recipe.instructions}")
    else:
        print(message)
