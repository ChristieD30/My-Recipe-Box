import unittest
import os
import sys
import tempfile
import shutil

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.model.recipes import Recipe
from app.model.users import User
from table_creation import create_tables

class TestRealDatabaseRequirements(unittest.TestCase):
    """Test requirements using real database with actual seed data from table_creation.py script"""
    
    @classmethod
    def setUpClass(cls):
        """Set up once for all tests - create real DB with seed data"""
        # Store test database in the test folder
        cls.test_dir = os.path.dirname(__file__)
        cls.test_db_path = os.path.join(cls.test_dir, 'test_recipe_box.db')
        
        print(f"Creating test database at: {cls.test_db_path}")
        
        # Create database with actual seed data using table_creation.py script
        success = create_tables(cls.test_db_path)
        if not success:
            raise Exception("Failed to create test database")
        
        # Set up Flask app to use test database
        cls.app = create_app(db_uri=f'sqlite:///{cls.test_db_path}')
        cls.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,
            'SECRET_KEY': 'test-secret-key'
        })
        
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create test client
        cls.client = cls.app.test_client()
        
        print("✅ Test database setup complete")
    
    @classmethod
    def tearDownClass(cls):
        """Clean up after all tests"""
        cls.app_context.pop()
        # Clean up test database file
        if os.path.exists(cls.test_db_path):
            os.remove(cls.test_db_path)
        print("🧹 Test database cleaned up")
    
    # ==========================================
    # SEED DATA VALIDATION TESTS
    # ==========================================
    
    def test_database_has_preloaded_recipes(self):
        """Test Case No. 1 - Test 1.1.0: Database contains prepopulated recipes"""
        with self.app.app_context():
            recipe_count = Recipe.query.count()
            
            # Should have all your seed recipes (check your actual count)
            self.assertGreaterEqual(recipe_count, 30, 
                                  f"Database should contain at least 30 recipes, found {recipe_count}")
            
            print(f"✅ Database contains {recipe_count} preloaded recipes")
    
    def test_seed_recipes_quality(self):
        """Test Case No. 2 - Test 1.1.0: Seed recipes have complete and realistic data"""
        with self.app.app_context():
            recipes = Recipe.query.all()
            
            self.assertGreater(len(recipes), 0, "Should have recipes in database")
            
            incomplete_recipes = []
            for recipe in recipes:
                issues = []
                
                # Check required fields
                if not recipe.name or len(recipe.name.strip()) <= 3:
                    issues.append("name too short")
                if not recipe.ingredients or len(recipe.ingredients.strip()) <= 10:
                    issues.append("ingredients too short")
                if not recipe.instructions or len(recipe.instructions.strip()) <= 20:
                    issues.append("instructions too short")
                if not recipe.category:
                    issues.append("missing category")
                
                if issues:
                    incomplete_recipes.append(f"{recipe.name}: {', '.join(issues)}")
            
            if incomplete_recipes:
                self.fail(f"Incomplete recipes found:\n" + "\n".join(incomplete_recipes))
            
            print(f"✅ All {len(recipes)} recipes have complete data")
    
    def test_recipes_organized_by_category(self):
        """Test Case No. 3 - Test 1.2.0: Recipes are organized by category"""
        with self.app.app_context():
            # Get all categories from your actual data
            all_recipes = Recipe.query.all()
            categories_in_db = set(recipe.category for recipe in all_recipes)
            
            print(f"Categories found in database: {sorted(categories_in_db)}")
            
            # Should have multiple categories
            self.assertGreater(len(categories_in_db), 3, 
                             f"Should have multiple categories, found: {categories_in_db}")
            
            # Test each category has recipes
            category_counts = {}
            for category in categories_in_db:
                recipes_in_category = Recipe.query.filter_by(category=category).all()
                category_counts[category] = len(recipes_in_category)
                
                self.assertGreater(len(recipes_in_category), 0, 
                                 f"Category '{category}' should have recipes")
            
            print("✅ Recipe categories:")
            for category, count in sorted(category_counts.items()):
                print(f"   {category}: {count} recipes")

if __name__ == '__main__':
    unittest.main(verbosity=2)