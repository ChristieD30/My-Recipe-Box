import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.service.user import RecipeService
from app.model.users import Recipe

class TestUserService(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'  # Use in-memory DB for tests
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

    
    def tearDown(self):
        """Run after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_recipe_success(self):
        """Test Case No. 4 - Test successful recipe creation"""
        result, message = RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Ingredient1, Ingredient2',
            instructions='Step 1, Step 2',
            category='Dessert',
            user_id=1
        )
        self.assertIsNotNone(result)
        self.assertEqual(message, "Recipe added successfully.")
        
        recipe = Recipe.query.filter_by(name='Test Recipe').first()
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.category, 'Dessert')
    
    def test_add_recipe_duplicate_name(self):
        """Test Case No. 5 - Test adding recipe with duplicate name returns error"""
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

    def test_recipe_with_image_display(self):
        """Test Case No. 6 - Test requirement 1.0.1: recipes with images display correctly"""
        result, message = RecipeService.add_recipe(
            name='Image Recipe',
            ingredients = "Test ingredients",
            instructions = "Test instructions",
            category = "Dessert",
            user_id = 1,
            image_location = "/static/uploads/test_image.jpg"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.image_location, "/static/uploads/test_image.jpg")
        
    def test_recipe_without_image_display(self):
        """Test Case No. 7 - Test requirement 1.0.1: recipes without images display correctly"""
        result, message = RecipeService.add_recipe(
            name='No Image Recipe',
            ingredients = "Test ingredients",
            instructions = "Test instructions",
            category = "Dessert",
            user_id = 1,
            image_location = None
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.image_location)

        