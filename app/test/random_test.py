# test_recipe_service.py
import unittest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.service.recipe import RecipeService
from app.model.users import User
from app.model.recipes import Recipe

class TestRecipeService(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        # Use in-memory database for tests
        self.app = create_app(database_uri='sqlite:///:memory:')
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create some test users
        self.user1 = User(
            username='testuser1',
            email='test1@example.com',
            name='Test User 1',
            password='password123'
        )
        self.user2 = User(
            username='testuser2',
            email='test2@example.com',
            name='Test User 2',
            password='password456'
        )
        db.session.add(self.user1)
        db.session.add(self.user2)
        db.session.commit()
        
        # Create some test recipes
        self.recipe1 = Recipe(
            name='Test Recipe 1',
            ingredients='1 cup flour\n2 eggs\n1 cup milk',
            instructions='1. Mix ingredients\n2. Cook until done',
            category='Breakfast',
            user_id=self.user1.id
        )
        self.recipe2 = Recipe(
            name='Test Recipe 2',
            ingredients='2 cups pasta\n1 jar sauce\n1 cup cheese',
            instructions='1. Cook pasta\n2. Add sauce\n3. Sprinkle cheese',
            category='Dinner',
            user_id=self.user2.id
        )
        self.recipe3 = Recipe(
            name='Test Recipe 3',
            ingredients='3 apples\n1 cup oats\n1/2 cup sugar',
            instructions='1. Slice apples\n2. Mix with oats\n3. Bake',
            category='Dessert',
            user_id=self.user1.id
        )
        db.session.add(self.recipe1)
        db.session.add(self.recipe2)
        db.session.add(self.recipe3)
        db.session.commit()
    
    def tearDown(self):
        """Run after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_get_random_recipe_with_recipes(self):
        """Test get_random_recipe returns a recipe when recipes exist"""
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
        
        # Assertions
        self.assertIsNotNone(recipe, "Recipe should not be None when recipes exist")
        self.assertIsInstance(recipe, Recipe, "Returned recipe should be a Recipe object")
        self.assertIsNotNone(message, "Message should not be None")
        
        # Check that no new users were created
        self.assertEqual(user_count_after, user_count_before, 
                        "No new users should be created during get_random_recipe()")
        
        # Verify the recipe is one of our test recipes
        recipe_ids = [self.recipe1.id, self.recipe2.id, self.recipe3.id]
        self.assertIn(recipe.id, recipe_ids, "Returned recipe should be one of the test recipes")
        
        # Print recipe details for debugging
        if recipe:
            print(f"{message} Recipe: {recipe.name} - Ingredients: {recipe.ingredients[:50]}... - Instructions: {recipe.instructions[:50]}...")
        else:
            print(message)

    def test_get_random_recipe_no_recipes(self):
        """Test get_random_recipe when no recipes exist"""
        # Remove all recipes
        Recipe.query.delete()
        db.session.commit()
        
        # Get users before fetching random recipe
        users_before = User.query.all()
        user_count_before = len(users_before)
        
        # Get random recipe
        recipe, message = RecipeService.get_random_recipe()
        
        # Get users after fetching random recipe
        users_after = User.query.all()
        user_count_after = len(users_after)
        
        # Assertions
        self.assertIsNone(recipe, "Recipe should be None when no recipes exist")
        self.assertIsNotNone(message, "Message should not be None")
        self.assertIn("No recipes", message, "Message should indicate no recipes available")
        
        # Check that no new users were created
        self.assertEqual(user_count_after, user_count_before, 
                        "No new users should be created during get_random_recipe()")
        
        print(f"No recipes test - Message: {message}")

    def test_get_random_recipe_user_count_stability(self):
        """Test that get_random_recipe doesn't affect user count"""
        # Get initial user count
        initial_user_count = User.query.count()
        
        # Call get_random_recipe multiple times
        for i in range(5):
            recipe, message = RecipeService.get_random_recipe()
            current_user_count = User.query.count()
            
            self.assertEqual(current_user_count, initial_user_count, 
                           f"User count changed on iteration {i+1}")
            
            if recipe:
                self.assertIsInstance(recipe, Recipe)
                print(f"Iteration {i+1}: Got recipe '{recipe.name}'")
            else:
                print(f"Iteration {i+1}: {message}")

    def test_get_random_recipe_returns_different_recipes(self):
        """Test that get_random_recipe can return different recipes"""
        recipes_found = set()
        
        # Try to get random recipes multiple times
        for i in range(10):
            recipe, message = RecipeService.get_random_recipe()
            if recipe:
                recipes_found.add(recipe.id)
        
        # With 3 recipes and 10 attempts, we should get at least 2 different recipes
        # (this is probabilistic, but very likely to pass)
        self.assertGreater(len(recipes_found), 1, 
                          "Should get different recipes across multiple calls")
        
        print(f"Found {len(recipes_found)} different recipes: {recipes_found}")

    def test_get_random_recipe_message_format(self):
        """Test that the message returned has expected format"""
        recipe, message = RecipeService.get_random_recipe()
        
        # Message should be a string
        self.assertIsInstance(message, str, "Message should be a string")
        self.assertGreater(len(message), 0, "Message should not be empty")
        
        if recipe:
            # If recipe exists, message might contain success information
            print(f"Success message: '{message}'")
        else:
            # If no recipe, message should indicate the issue
            self.assertIn("No", message, "No-recipe message should contain 'No'")
            print(f"No-recipe message: '{message}'")

    def test_get_random_recipe_recipe_attributes(self):
        """Test that returned recipe has all expected attributes"""
        recipe, message = RecipeService.get_random_recipe()
        
        if recipe:
            # Check that recipe has all required attributes
            self.assertTrue(hasattr(recipe, 'id'), "Recipe should have id")
            self.assertTrue(hasattr(recipe, 'name'), "Recipe should have name")
            self.assertTrue(hasattr(recipe, 'ingredients'), "Recipe should have ingredients")
            self.assertTrue(hasattr(recipe, 'instructions'), "Recipe should have instructions")
            self.assertTrue(hasattr(recipe, 'category'), "Recipe should have category")
            self.assertTrue(hasattr(recipe, 'user_id'), "Recipe should have user_id")
            
            # Check that attributes have values
            self.assertIsNotNone(recipe.name, "Recipe name should not be None")
            self.assertIsNotNone(recipe.ingredients, "Recipe ingredients should not be None")
            self.assertIsNotNone(recipe.instructions, "Recipe instructions should not be None")
            
            print(f"Recipe attributes verified for: {recipe.name}")
        else:
            print(f"No recipe to verify attributes: {message}")

if __name__ == '__main__':
    unittest.main(verbosity=2)