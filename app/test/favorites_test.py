# test_favorite_service.py
import unittest
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app, db
from app.service.favorites import FavoriteService
from app.service.user import UserService
from app.service.recipe import RecipeService
from app.model.users import User
from app.model.recipes import Recipe
from app.model.favorites import Favorite

class TestFavoriteService(unittest.TestCase):
    def setUp(self):
        """Run before each test"""
        # Use in-memory database for tests
        self.app = create_app(database_uri='sqlite:///:memory:')
        self.app.config['TESTING'] = True
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        
        # Create test users
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
        
        # Create test recipes
        self.recipe1 = Recipe(
            name='Test Recipe 1',
            ingredients='Test ingredients 1',
            instructions='Test instructions 1',
            category='Breakfast',
            user_id=self.user1.id
        )
        self.recipe2 = Recipe(
            name='Test Recipe 2',
            ingredients='Test ingredients 2',
            instructions='Test instructions 2',
            category='Lunch',
            user_id=self.user2.id
        )
        self.recipe3 = Recipe(
            name='Test Recipe 3',
            ingredients='Test ingredients 3',
            instructions='Test instructions 3',
            category='Dinner',
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

    def test_add_favorite_success(self):
        """Test Case No. 01 successfully adding a recipe to favorites"""
        result = FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        
        self.assertIsInstance(result, Favorite)
        self.assertEqual(result.user_id, self.user1.id)
        self.assertEqual(result.recipe_id, self.recipe1.id)
        
        # Verify it was saved to database
        favorite_in_db = Favorite.query.filter_by(
            user_id=self.user1.id, 
            recipe_id=self.recipe1.id
        ).first()
        self.assertIsNotNone(favorite_in_db)

    def test_add_favorite_duplicate(self):
        """Test Case No. 02 - adding a recipe that's already favorited returns existing favorite"""
        # Add favorite first time
        result1 = FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        self.assertIsInstance(result1, Favorite)
        
        # Add same favorite again
        result2 = FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        self.assertIsInstance(result2, Favorite)
        self.assertEqual(result1.id, result2.id)  # Should return the same favorite
        
        # Verify only one favorite exists in database
        favorites_count = Favorite.query.filter_by(
            user_id=self.user1.id, 
            recipe_id=self.recipe1.id
        ).count()
        self.assertEqual(favorites_count, 1)

    def test_add_favorite_different_users(self):
        """Test Case No. 03 - different users can favorite the same recipe"""
        # User 1 favorites recipe 1
        result1 = FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        self.assertIsInstance(result1, Favorite)
        
        # User 2 favorites same recipe
        result2 = FavoriteService.add_favorite(self.recipe1.id, self.user2.id)
        self.assertIsInstance(result2, Favorite)
        
        # Both should be different favorites
        self.assertNotEqual(result1.id, result2.id)
        
        # Verify both exist in database
        user1_favorite = Favorite.query.filter_by(
            user_id=self.user1.id, 
            recipe_id=self.recipe1.id
        ).first()
        user2_favorite = Favorite.query.filter_by(
            user_id=self.user2.id, 
            recipe_id=self.recipe1.id
        ).first()
        
        self.assertIsNotNone(user1_favorite)
        self.assertIsNotNone(user2_favorite)

    def test_add_favorite_multiple_recipes(self):
        """Test Case No. 04 - user can favorite multiple recipes"""
        result1 = FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        result2 = FavoriteService.add_favorite(self.recipe2.id, self.user1.id)
        result3 = FavoriteService.add_favorite(self.recipe3.id, self.user1.id)
        
        self.assertIsInstance(result1, Favorite)
        self.assertIsInstance(result2, Favorite)
        self.assertIsInstance(result3, Favorite)
        
        # Verify all three favorites exist
        favorites_count = Favorite.query.filter_by(user_id=self.user1.id).count()
        self.assertEqual(favorites_count, 3)

    def test_remove_favorite_success(self):
        """Test Case No. 05 - successfully removing a favorite"""
        # Add favorite first
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        
        # Verify it exists
        self.assertTrue(FavoriteService.is_favorite(self.recipe1.id, self.user1.id))
        
        # Remove favorite
        result = FavoriteService.remove_favorite(self.recipe1.id, self.user1.id)
        self.assertTrue(result)
        
        # Verify it was removed
        self.assertFalse(FavoriteService.is_favorite(self.recipe1.id, self.user1.id))
        
        # Verify it's gone from database
        favorite_in_db = Favorite.query.filter_by(
            user_id=self.user1.id, 
            recipe_id=self.recipe1.id
        ).first()
        self.assertIsNone(favorite_in_db)

    def test_remove_favorite_nonexistent(self):
        """Test Case No. 06 - removing a favorite that doesn't exist returns False"""
        result = FavoriteService.remove_favorite(self.recipe1.id, self.user1.id)
        self.assertFalse(result)

    def test_remove_favorite_wrong_user(self):
        """Test Case No. 07 - removing favorite by wrong user returns False"""
        # User 1 adds favorite
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        
        # User 2 tries to remove user 1's favorite
        result = FavoriteService.remove_favorite(self.recipe1.id, self.user2.id)
        self.assertFalse(result)
        
        # Verify user 1's favorite still exists
        self.assertTrue(FavoriteService.is_favorite(self.recipe1.id, self.user1.id))

    def test_is_favorite_true(self):
        """Test Case No. 08 - is_favorite returns True for favorited recipe"""
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        result = FavoriteService.is_favorite(self.recipe1.id, self.user1.id)
        self.assertTrue(result)

    def test_is_favorite_false(self):
        """Test Case No. 09 - is_favorite returns False for non-favorited recipe"""
        result = FavoriteService.is_favorite(self.recipe1.id, self.user1.id)
        self.assertFalse(result)

    def test_is_favorite_different_user(self):
        """Test Case No. 10 - is_favorite returns False for different user"""
        # User 1 favorites recipe
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        
        # Check if user 2 has favorited it (should be False)
        result = FavoriteService.is_favorite(self.recipe1.id, self.user2.id)
        self.assertFalse(result)

    def test_is_favorite_nonexistent_recipe(self):
        """Test Case No. 11 - is_favorite returns False for nonexistent recipe"""
        result = FavoriteService.is_favorite(99999, self.user1.id)
        self.assertFalse(result)

    def test_is_favorite_nonexistent_user(self):
        """Test Case No. 12 - is_favorite returns False for nonexistent user"""
        result = FavoriteService.is_favorite(self.recipe1.id, 99999)
        self.assertFalse(result)

    def test_get_user_favorites_empty(self):
        """Test Case No. 13 - get_user_favorites returns empty list when user has no favorites"""
        favorites = FavoriteService.get_user_favorites(self.user1.id)
        self.assertEqual(len(favorites), 0)
        self.assertEqual(favorites, [])

    def test_get_user_favorites_single(self):
        """Test Case No. 14 - get_user_favorites returns single favorite"""
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        
        favorites = FavoriteService.get_user_favorites(self.user1.id)
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0].recipe_id, self.recipe1.id)
        self.assertEqual(favorites[0].user_id, self.user1.id)

    def test_get_user_favorites_multiple(self):
        """Test Case No. 15 - get_user_favorites returns all user's favorites"""
        # User 1 favorites multiple recipes
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        FavoriteService.add_favorite(self.recipe2.id, self.user1.id)
        FavoriteService.add_favorite(self.recipe3.id, self.user1.id)
        
        favorites = FavoriteService.get_user_favorites(self.user1.id)
        self.assertEqual(len(favorites), 3)
        
        # Check all recipe IDs are present
        recipe_ids = [fav.recipe_id for fav in favorites]
        self.assertIn(self.recipe1.id, recipe_ids)
        self.assertIn(self.recipe2.id, recipe_ids)
        self.assertIn(self.recipe3.id, recipe_ids)

    def test_get_user_favorites_different_users(self):
        """Test Case No. 16 - get_user_favorites only returns favorites for specific user"""
        # Both users favorite different recipes
        FavoriteService.add_favorite(self.recipe1.id, self.user1.id)
        FavoriteService.add_favorite(self.recipe2.id, self.user1.id)
        FavoriteService.add_favorite(self.recipe2.id, self.user2.id)
        FavoriteService.add_favorite(self.recipe3.id, self.user2.id)
        
        # Check user 1's favorites
        user1_favorites = FavoriteService.get_user_favorites(self.user1.id)
        self.assertEqual(len(user1_favorites), 2)
        user1_recipe_ids = [fav.recipe_id for fav in user1_favorites]
        self.assertIn(self.recipe1.id, user1_recipe_ids)
        self.assertIn(self.recipe2.id, user1_recipe_ids)
        self.assertNotIn(self.recipe3.id, user1_recipe_ids)
        
        # Check user 2's favorites
        user2_favorites = FavoriteService.get_user_favorites(self.user2.id)
        self.assertEqual(len(user2_favorites), 2)
        user2_recipe_ids = [fav.recipe_id for fav in user2_favorites]
        self.assertIn(self.recipe2.id, user2_recipe_ids)
        self.assertIn(self.recipe3.id, user2_recipe_ids)
        self.assertNotIn(self.recipe1.id, user2_recipe_ids)

    def test_get_user_favorites_nonexistent_user(self):
        """Test Case No. 17 - get_user_favorites returns empty list for nonexistent user"""
        favorites = FavoriteService.get_user_favorites(99999)
        self.assertEqual(len(favorites), 0)

    def test_favorite_workflow(self):
        """Test Case No. 18 -  complete workflow: add, check, remove, check"""
        user_id = self.user1.id
        recipe_id = self.recipe1.id
        
        # Initially not favorited
        self.assertFalse(FavoriteService.is_favorite(recipe_id, user_id))
        
        # Add to favorites
        result = FavoriteService.add_favorite(recipe_id, user_id)
        self.assertIsInstance(result, Favorite)
        
        # Should now be favorited
        self.assertTrue(FavoriteService.is_favorite(recipe_id, user_id))
        
        # Should appear in user's favorites list
        favorites = FavoriteService.get_user_favorites(user_id)
        self.assertEqual(len(favorites), 1)
        self.assertEqual(favorites[0].recipe_id, recipe_id)
        
        # Remove from favorites
        remove_result = FavoriteService.remove_favorite(recipe_id, user_id)
        self.assertTrue(remove_result)
        
        # Should no longer be favorited
        self.assertFalse(FavoriteService.is_favorite(recipe_id, user_id))
        
        # Should not appear in user's favorites list
        favorites_after = FavoriteService.get_user_favorites(user_id)
        self.assertEqual(len(favorites_after), 0)

if __name__ == '__main__':
    unittest.main(verbosity=2)