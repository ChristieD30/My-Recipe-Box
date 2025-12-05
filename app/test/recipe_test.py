import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.service.recipe import RecipeService
from app.model.recipes import Recipe
from app.model.users import User

class TestRecipeService(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        # Use in-memory database for tests
        self.app = create_app(database_uri='sqlite:///:memory:')
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create a test user for recipes
        self.test_user = User(
            username='testuser',
            email='test@example.com',
            name='Test User',
            password='testpassword'
        )
        db.session.add(self.test_user)
        db.session.commit()

    
    def tearDown(self):
        """Run after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_add_recipe_success(self):
        """Test Case No. 22 - Test successful recipe creation"""
        result, message = RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Ingredient1, Ingredient2',
            instructions='Step 1, Step 2',
            category='Dessert',
            user_id=self.test_user.id
        )
        self.assertIsNotNone(result)
        self.assertEqual(message, "Your recipe 'Test Recipe' is added.")
        
        recipe = Recipe.query.filter_by(name='Test Recipe').first()
        self.assertIsNotNone(recipe)
        self.assertEqual(recipe.category, 'Dessert')
    
    def test_add_recipe_duplicate_name(self):
        """Test Case No. 23 - Test adding recipe with duplicate name returns error"""
        # Add first recipe
        RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Ingredient1, Ingredient2',
            instructions='Step 1, Step 2',
            category='Dessert',
            user_id=self.test_user.id
        )
        
        # Try to add recipe with same name
        result, message = RecipeService.add_recipe(
            name='Test Recipe',
            ingredients='Different ingredients',
            instructions='Different instructions',
            category='Dessert',
            user_id=self.test_user.id
        )
        
        # Should return None and error message
        self.assertIsNone(result)
        self.assertEqual(message, "Recipe name already exists. Please rename it.")

    def test_recipe_with_image_display(self):
        """Test Case No. 24 - Test requirement 1.0.1: recipes with images display correctly"""
        result, message = RecipeService.add_recipe(
            name='Image Recipe',
            ingredients = "Test ingredients",
            instructions = "Test instructions",
            category = "Dessert",
            user_id=self.test_user.id,
            image_location="test_image.jpg"
        )
        self.assertIsNotNone(result)
        self.assertEqual(result.image_location, "test_image.jpg")
        
    def test_recipe_without_image_display(self):
        """Test Case No. 25 - Test requirement 1.0.1: recipes without images display correctly"""
        result, message = RecipeService.add_recipe(
            name='No Image Recipe',
            ingredients = "Test ingredients",
            instructions = "Test instructions",
            category = "Dessert",
            user_id = self.test_user.id,
            image_location = None
        )
        self.assertIsNotNone(result)
        self.assertIsNone(result.image_location)

    # ==========================================
    # SEARCH FUNCTIONALITY TESTS (Backend Service)
    # ==========================================
    
    def test_search_recipes_by_name(self):
        """Test Case No. 26 - Test 3.0.0: Search recipes by name"""
        # Create test recipes with distinct names
        result1, msg1 = RecipeService.add_recipe(
            name='Chocolate Cake',
            ingredients='Flour, Sugar, Cocoa',
            instructions='Mix and bake',
            category='Dessert',
            user_id=self.test_user.id
        )
        self.assertIsNotNone(result1, f"Failed to create first recipe: {msg1}")
        
        result2, msg2 = RecipeService.add_recipe(
            name='Vanilla Cookies',
            ingredients='Flour, Sugar, Vanilla',
            instructions='Mix and bake',
            category='Dessert', 
            user_id=self.test_user.id
        )
        self.assertIsNotNone(result2, f"Failed to create second recipe: {msg2}")
        
        result3, msg3 = RecipeService.add_recipe(
            name='Strawberry Smoothie',
            ingredients='Strawberries, Milk, Sugar',
            instructions='Blend ingredients',
            category='Snacks',
            user_id=self.test_user.id
        )
        self.assertIsNotNone(result3, f"Failed to create third recipe: {msg3}")
        
        # Verify recipes were created
        all_recipes = Recipe.query.all()
        self.assertEqual(len(all_recipes), 3, f"Expected 3 recipes, got {len(all_recipes)}")
        
        # Search by name - should find chocolate cake
        results = RecipeService.search_recipes(query='chocolate')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Chocolate Cake')
        
        # Search by partial name - should find cookies
        results = RecipeService.search_recipes(query='cook')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Vanilla Cookies')
        
        # Case insensitive search - should find smoothie
        results = RecipeService.search_recipes(query='SMOOTHIE')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Strawberry Smoothie')
    
    def test_search_recipes_by_ingredients(self):
        """Test Case No. 27 - Test 3.0.1: Search recipes by ingredients"""
        # Create test recipes with distinct ingredients
        RecipeService.add_recipe(
            name='Tomato Pasta',
            ingredients='Pasta, Tomatoes, Basil, Garlic',
            instructions='Cook pasta, add sauce',
            category='Dinner',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Caesar Salad',
            ingredients='Lettuce, Croutons, Parmesan, Caesar Dressing',
            instructions='Toss ingredients',
            category='Salads',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Garlic Bread',
            ingredients='Bread, Butter, Garlic, Parsley',
            instructions='Mix butter with garlic, spread on bread, bake',
            category='Snacks',
            user_id=self.test_user.id
        )
        
        # Search by ingredient - should find tomato pasta
        results = RecipeService.search_recipes(query='tomatoes')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Tomato Pasta')
        
        # Search by common ingredient - should find pasta and bread (both have garlic)
        results = RecipeService.search_recipes(query='garlic')
        self.assertEqual(len(results), 2)
        recipe_names = [r.name for r in results]
        self.assertIn('Tomato Pasta', recipe_names)
        self.assertIn('Garlic Bread', recipe_names)
        
        # Case insensitive ingredient search - should find salad
        results = RecipeService.search_recipes(query='PARMESAN')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Caesar Salad')
    
    def test_search_recipes_by_category(self):
        """Test Case No. 28 - Test search recipes by category"""

        RecipeService.add_recipe(
            name='Apple Pie',
            ingredients='Apples, Flour, Sugar, Butter',
            instructions='Make pie crust, fill with apples, bake',
            category='Dessert',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Chocolate Mousse',
            ingredients='Chocolate, Cream, Sugar, Eggs',
            instructions='Melt chocolate, whip cream, combine',
            category='Dessert',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Grilled Chicken',
            ingredients='Chicken, Oil, Spices',
            instructions='Season chicken, grill until cooked',
            category='Lunch',
            user_id=self.test_user.id
        )
        
        # Search by category - should find desserts
        results = RecipeService.search_recipes(query='dessert')
        self.assertEqual(len(results), 2)
        recipe_names = [r.name for r in results]
        self.assertIn('Apple Pie', recipe_names)
        self.assertIn('Chocolate Mousse', recipe_names)
        
        # Search by partial category - should find lunch
        results = RecipeService.search_recipes(query='lunch')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Grilled Chicken')
    
    def test_search_recipes_no_results(self):
        """Test Case No. 29 - Test search with no matching results"""
        # Create one recipe
        RecipeService.add_recipe(
            name='Simple Salad',
            ingredients='Lettuce, Tomatoes',
            instructions='Mix ingredients',
            category='Salads',
            user_id=self.test_user.id
        )
        
        # Search for something that doesn't exist
        results = RecipeService.search_recipes(query='pizza')
        self.assertEqual(len(results), 0)
        
        # Search for empty string should return all recipes
        results = RecipeService.search_recipes(query='')
        self.assertEqual(len(results), 1)
        
        # Search with None query should return all recipes
        results = RecipeService.search_recipes(query=None)
        self.assertEqual(len(results), 1)
    
    def test_search_recipes_multiple_matches(self):
        """Test Case No. 30 - Test search returning multiple matches across different fields"""
        # Create recipes where search term appears in different fields
        RecipeService.add_recipe(
            name='Lemon Cake',  # 'lemon' in name
            ingredients='Flour, Sugar, Eggs, Butter',
            instructions='Mix and bake',
            category='Dessert',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Fish Dinner',
            ingredients='Fish, Lemon, Herbs',  # 'lemon' in ingredients
            instructions='Season fish with lemon and herbs',
            category='Dinner',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Herb Chicken',
            ingredients='Chicken, Herbs, Spices, Lemon',
            instructions='Cook chicken with herbs and lemon',
            category='Dinner', 
            user_id=self.test_user.id
        )
        
        # Search for 'lemon' - should find all three recipes
        results = RecipeService.search_recipes(query='lemon')
        self.assertEqual(len(results), 3)
        
        recipe_names = [r.name for r in results]
        self.assertIn('Lemon Cake', recipe_names)
        self.assertIn('Fish Dinner', recipe_names)
        self.assertIn('Herb Chicken', recipe_names)
    
    def test_search_recipes_with_category_filter(self):
        """Test Case No. 31 - Test search with both query and category filter"""
        # Create recipes in different categories
        RecipeService.add_recipe(
            name='Chocolate Dessert',
            ingredients='Chocolate, Sugar',
            instructions='Mix and serve',
            category='Dessert',
            user_id=self.test_user.id
        )
        RecipeService.add_recipe(
            name='Chocolate Smoothie',
            ingredients='Chocolate, Milk',
            instructions='Blend ingredients',
            category='Snacks',
            user_id=self.test_user.id
        )
        
        # Search for chocolate in dessert category only
        results = RecipeService.search_recipes(query='chocolate', category='Dessert')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Chocolate Dessert')
        
        # Search for chocolate in beverage category only
        results = RecipeService.search_recipes(query='chocolate', category='Snacks')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Chocolate Smoothie')
        
        # Search with category filter only
        results = RecipeService.search_recipes(category='Dessert')
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].name, 'Chocolate Dessert')

        