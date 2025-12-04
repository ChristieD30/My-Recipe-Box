import unittest
import json
import os
import tempfile
from app import create_app, db
from app.model.users import User
from app.model.recipes import Recipe
from werkzeug.security import generate_password_hash

class TestFlaskRoutes(unittest.TestCase):
    
    def setUp(self):
        """Set up test database and client before each test"""
        # Create test app with in-memory database
        self.app = create_app(db_uri='sqlite:///:memory:')
        
        # Configure for testing
        self.app.config.update({
            'TESTING': True,
            'WTF_CSRF_ENABLED': False,  # Disable CSRF for testing
            'SECRET_KEY': 'test-secret-key',
            'LOGIN_DISABLED': False
        })
        
        # Create application context
        self.app_context = self.app.app_context()
        self.app_context.push()
        
        # Create test client
        self.client = self.app.test_client()
        
        # Create tables
        with self.app.app_context():
            db.create_all()
            
            # Create test user
            self.test_user = User(
                username='testuser',
                email='test@example.com',
                name='Test User',
                password=generate_password_hash('testpass123')
            )
            db.session.add(self.test_user)
            db.session.commit()
            self.user_id = self.test_user.id
            
            # Create test recipe
            self.test_recipe = Recipe(
                name='Test Recipe',
                ingredients='Test ingredients',
                instructions='Test instructions',
                category='Test',
                user_id=self.user_id
            )
            db.session.add(self.test_recipe)
            db.session.commit()
            self.recipe_id = self.test_recipe.id
    
    def tearDown(self):
        """Clean up after each test"""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()
    
    def login_test_user(self):
        """Helper method to log in the test user"""
        with self.client.session_transaction() as sess:
            sess['user_id'] = self.user_id
            sess['username'] = 'testuser'
        return True
    
    # ==========================================
    # 1. STATIC ROUTE TESTS
    # ==========================================
    
    def test_home_page_loads(self):
        """Test Case No. 8 - Test GET / - Home page"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data)  # Basic HTML check
    
    def test_about_page_loads(self):
        """Test Case No. 9 - Test GET /about - About page"""
        response = self.client.get('/about')
        
        self.assertEqual(response.status_code, 200)
    
    def test_faq_page_loads(self):
        """Test Case No. 10 - Test GET /faq - FAQ page"""
        response = self.client.get('/faq')
        
        self.assertEqual(response.status_code, 200)
    
    def test_help_page_loads(self):
        """Test Case No. 11 - Test GET /help - Help page (should be same as FAQ)"""
        response = self.client.get('/help')
        
        self.assertEqual(response.status_code, 200)
    
    # ==========================================
    # 2. AUTHENTICATION ROUTE TESTS
    # ==========================================
    
    def test_login_page_get(self):
        """Test Case No. 12 - Test GET /login - Login form display"""
        response = self.client.get('/login')
        
        self.assertEqual(response.status_code, 200)
        # Check for login form elements
        self.assertIn(b'username', response.data.lower())
        self.assertIn(b'password', response.data.lower())
    
    def test_login_post_success(self):
        """Test Case No. 13 - Test POST /login - Successful login"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Should redirect or show success
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_post_failure(self):
        """Test Case No. 14 - Test POST /login - Failed login"""
        response = self.client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        
        # Should show error or redirect back
        self.assertIn(response.status_code, [200, 302, 401])
    
    def test_signup_page_get(self):
        """Test Case No. 15 - Test GET /signup - Registration form display"""
        response = self.client.get('/signup')
        
        self.assertEqual(response.status_code, 200)
    
    def test_add_user_post_success(self):
        """Test Case No. 16 - Test POST /add_user - User registration"""
        response = self.client.post('/add_user', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123'
        })
        
        self.assertIn(response.status_code, [200, 302])
        
        # Verify user was created
        new_user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, 'newuser@example.com')
    
    def test_logout_post(self):
        """Test Case No. 17 - Test POST /logout - User logout"""
        # Login first
        self.login_test_user()
        
        response = self.client.post('/logout', follow_redirects=True)
        
        self.assertIn(response.status_code, [200, 302])
    
    # ==========================================
    # 3. RECIPE BROWSING TESTS
    # ==========================================
    
    def test_browse_recipes_page(self):
        """Test Case No. 18 - Test GET /browse_recipes - Recipe browsing page"""
        response = self.client.get('/browse_recipes')
        
        self.assertEqual(response.status_code, 200)
    
    def test_show_recipe_with_valid_id(self):
        """Test Case No. 19 - Test GET /show_recipe?recipe_id=X - Valid recipe display"""
        response = self.client.get(f'/show_recipe?recipe_id={self.recipe_id}')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Recipe', response.data)
    
    def test_show_recipe_with_invalid_id(self):
        """Test Case No. 20 - Test GET /show_recipe?recipe_id=999 - Invalid recipe ID"""
        response = self.client.get('/show_recipe?recipe_id=999999')
        
        # Should handle gracefully (404, error page, or redirect)
        self.assertIn(response.status_code, [200, 404, 302])
    
    def test_featured_recipe_page(self):
        """Test Case No. 21 - Test GET /featured - Featured/random recipe"""
        response = self.client.get('/featured')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_page_get(self):
        """Test Case No. 22 - Test GET /search - Search form display"""
        response = self.client.get('/search')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_with_query(self):
        """Test Case No. 23 - Test GET /search?q=test - Search with query"""
        response = self.client.get('/search?q=test')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_post(self):
        """Test Case No. 24 - Test POST /search - Search form submission"""
        response = self.client.post('/search', data={
            'query': 'test'
        })
        
        self.assertEqual(response.status_code, 200)
    
    # ==========================================
    # 4. API ENDPOINT TESTS  
    # ==========================================
    
    def test_random_recipe_api(self):
        """Test Case No. 25 - Test GET /random_recipe - Random recipe API"""
        response = self.client.get('/random_recipe')
        
        self.assertEqual(response.status_code, 200)
        # Should return JSON
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    def test_browse_recipes_list_api(self):
        """Test Case No. 26 - Test GET /browse_recipes_list - Recipe list API"""
        response = self.client.get('/browse_recipes_list')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    def test_search_results_api(self):
        """Test Case No. 27 - Test GET /search_results?q=test - Search API"""
        response = self.client.get('/search_results?q=test')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    def test_get_recipe_by_id_api(self):
        """Test Case No. 28 - Test GET /get_recipe/<id> - Recipe by ID API"""
        response = self.client.get(f'/get_recipe/{self.recipe_id}')
        
        self.assertEqual(response.status_code, 200)
    
    def test_current_user_api(self):
        """Test Case No. 29 - Test GET /current_user - Current user API"""
        response = self.client.get('/current_user')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    # ==========================================
    # 5. PROTECTED ROUTE TESTS (Login Required)
    # ==========================================
    
    def test_add_recipes_requires_login(self):
        """Test Case No. 30 - Test GET /add_recipes without login - Should be blocked"""
        response = self.client.get('/add_recipes')
        
        # Should redirect to login or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_add_recipes_with_login(self):
        """Test Case No. 31 - Test GET /add_recipes with login - Should work"""
        self.login_test_user()
        
        response = self.client.get('/add_recipes')
        
        self.assertEqual(response.status_code, 200)
    
    def test_add_recipe_post_with_login(self):
        """Test Case No. 32 - Test POST /add_recipe - Create new recipe"""
        self.login_test_user()
        
        recipe_data = {
            'name': 'New Test Recipe',
            'ingredients': 'New ingredients',
            'instructions': 'New instructions',
            'category': 'Test'
        }
        
        response = self.client.post('/add_recipe', data=recipe_data)
        
        self.assertIn(response.status_code, [200, 302])
        
        # Verify recipe was created
        new_recipe = Recipe.query.filter_by(name='New Test Recipe').first()
        self.assertIsNotNone(new_recipe)
    
    def test_favorites_requires_login(self):
        """Test Case No. 33 - Test GET /favorites without login - Should be blocked"""
        response = self.client.get('/favorites')
        
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_favorites_with_login(self):
        """Test Case No. 34 - Test GET /favorites with login - Should work"""
        self.login_test_user()
        
        response = self.client.get('/favorites')
        
        self.assertEqual(response.status_code, 200)
    
    def test_display_page_with_login(self):
        """Test Case No. 35 - Test GET /display with login - Recipe management page"""
        self.login_test_user()
        
        response = self.client.get('/display')
        
        self.assertEqual(response.status_code, 200)
    
    # ==========================================
    # 6. FAVORITES FUNCTIONALITY TESTS
    # ==========================================
    
    def test_add_favorite_post(self):
        """Test Case No. 36 - Test POST /add_favorite - Add recipe to favorites"""
        self.login_test_user()
        
        response = self.client.post('/add_favorite', json={
            'recipe_id': self.recipe_id
        })
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_remove_favorite_post(self):
        """Test Case No. 37 - Test POST /remove_favorite - Remove from favorites"""
        self.login_test_user()
        
        response = self.client.post('/remove_favorite', json={
            'recipe_id': self.recipe_id
        })
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_is_favorite_api(self):
        """Test Case No. 38 - Test GET /is_favorite/<id> - Check if recipe is favorited"""
        self.login_test_user()
        
        response = self.client.get(f'/is_favorite/{self.recipe_id}')
        
        self.assertEqual(response.status_code, 200)
    
    def test_favorites_list_api(self):
        """Test Case No. 39 - Test GET /favorites_list - Get user's favorites"""
        self.login_test_user()
        
        response = self.client.get('/favorites_list')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    # ==========================================
    # 7. ERROR HANDLING TESTS
    # ==========================================
    
    def test_nonexistent_route(self):
        """Test Case No. 40 - Test accessing non-existent route - Should return 404"""
        response = self.client.get('/nonexistent-route')
        
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_method_on_route(self):
        """Test Case No. 41 - Test using wrong HTTP method - Should return 405"""
        # Try POST on a GET-only route
        response = self.client.post('/about')
        
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()