import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.service.recipe import RecipeService
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

    
    def tearDown(self):
        """Run after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_recipe_success(self):
        """Test successful recipe creation"""
        recipe_name = 'Test Recipe'
        result, message = RecipeService.add_recipe(
            name=recipe_name,
            ingredients='Ingredient1, Ingredient2',
            instructions='Step 1, Step 2',
            category='Dessert',
            user_id=1
        )
        self.assertIsNotNone(result)
        self.assertEqual(message, f"Your recipe '{recipe_name}' is added.")
        
        recipe = Recipe.query.filter_by(name='Test Recipe').first()
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.category, 'Dessert')
    
    def test_add_recipe_duplicate_name(self):
        """Test adding recipe with duplicate name returns error"""
        # Add first recipe
        RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Ingredient1, Ingredient2',
            instructions='Step 1, Step 2',
            category='Dessert',
            user_id=1
        )
        
        # Try to add second recipe with same name
        result, message = RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Ingredient3, Ingredient4',
            instructions='Step A, Step B',
            category='Dessert',
            user_id=1
        )
        
        # Should return None and error message
        self.assertIsNone(result)
        self.assertEqual(message, "Recipe name already exists. Please rename it.")
        