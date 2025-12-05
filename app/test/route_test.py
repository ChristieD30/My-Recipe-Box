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
        self.app = create_app(database_uri='sqlite:///:memory:')
        
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
                category='Dessert',
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
            sess['email'] = 'test@example.com'
            sess['name'] = 'Test User'
            sess['logged_in'] = True
        return True
    
    # ==========================================
    # 1. ABOUT/FAQ/HOME PAGE ROUTE TESTS
    # ==========================================
    
    def test_home_page_loads(self):
        """Test Case No. 32 - Test GET / - Home page"""
        response = self.client.get('/')
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'html', response.data)  # Basic HTML check
    
    def test_about_page_loads(self):
        """Test Case No. 33 - Test GET /about - About page"""
        response = self.client.get('/about')
        
        self.assertEqual(response.status_code, 200)
    
    def test_faq_page_loads(self):
        """Test Case No. 34 - Test GET /faq - FAQ page"""
        response = self.client.get('/faq')
        
        self.assertEqual(response.status_code, 200)
    
    # ==========================================
    # 2. AUTHENTICATION ROUTE TESTS
    # ==========================================
    
    def test_login_page_get(self):
        """Test Case No. 35 - Test GET /login - Login form display"""
        response = self.client.get('/login')
        
        self.assertEqual(response.status_code, 200)
        # Check for login form elements
        self.assertIn(b'username', response.data.lower())
        self.assertIn(b'password', response.data.lower())
    
    def test_login_post_success(self):
        """Test Case No. 36 - Test POST /login - Successful login"""
        response = self.client.post('/login', data={
            'username': 'testuser',
            'password': 'testpass123'
        }, follow_redirects=True)
        
        # Should redirect or show success
        self.assertIn(response.status_code, [200, 302])
    
    def test_login_post_failure(self):
        """Test Case No. 37 - Test POST /login - Failed login"""
        response = self.client.post('/login', data={
            'username': 'wronguser',
            'password': 'wrongpass'
        })
        
        # Should show error or redirect back
        self.assertIn(response.status_code, [200, 302, 401])
    
    def test_signup_page_get(self):
        """Test Case No. 38 - Test GET /signup - Registration form display"""
        response = self.client.get('/signup')
        
        self.assertEqual(response.status_code, 200)
    
    def test_add_user_post_success(self):
        """Test Case No. 39 - Test POST /add_user - User registration"""
        response = self.client.post('/add_user', data={
            'username': 'newuser',
            'email': 'newuser@example.com',
            'name': 'New User',
            'password': 'newpass123'
        })
        
        self.assertIn(response.status_code, [200, 201, 302])
        
        # Verify user was created
        new_user = User.query.filter_by(username='newuser').first()
        self.assertIsNotNone(new_user)
        self.assertEqual(new_user.email, 'newuser@example.com')
    
    def test_logout_post(self):
        """Test Case No. 40 - Test POST /logout - User logout"""
        # Login first
        self.login_test_user()
        
        response = self.client.post('/logout', follow_redirects=True)
        
        self.assertIn(response.status_code, [200, 302])
    
    # ==========================================
    # 3. RECIPE BROWSING TESTS
    # ==========================================
    
    def test_browse_recipes_page(self):
        """Test Case No. 41 - Test GET /browse_recipes - Recipe browsing page"""
        response = self.client.get('/browse_recipes')
        
        self.assertEqual(response.status_code, 200)
    
    def test_show_recipe_with_valid_id(self):
        """Test Case No. 42 - Test GET /show_recipe?recipe_id=X - Valid recipe display"""
        response = self.client.get(f'/show_recipe?recipe_id={self.recipe_id}')
        
        self.assertEqual(response.status_code, 200)
        # The template loads recipe data via JavaScript, so initial response shows loading message
        self.assertIn(b'Loading recipe...', response.data)
    
    def test_show_recipe_with_invalid_id(self):
        """Test Case No. 43 - Test GET /show_recipe?recipe_id=999 - Invalid recipe ID"""
        response = self.client.get('/show_recipe?recipe_id=999999')
        
        # Should handle gracefully (404, error page, or redirect)
        self.assertIn(response.status_code, [200, 404, 302])
    
    def test_featured_recipe_page(self):
        """Test Case No. 44 - Test GET /featured - Featured/random recipe"""
        response = self.client.get('/featured')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_page_get(self):
        """Test Case No. 45 - Test GET /search - Search form display"""
        response = self.client.get('/search')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_with_query(self):
        """Test Case No. 46 - Test GET /search?q=test - Search with query"""
        response = self.client.get('/search?q=test')
        
        self.assertEqual(response.status_code, 200)
    
    def test_search_post(self):
        """Test Case No. 47 - Test POST /search - Search form submission without favorites"""
        response = self.client.post('/search', data={
            'query': 'test'
        })
        
        # Should redirect when no favorite action is provided
        self.assertEqual(response.status_code, 302)

    # ==========================================
    # 4. API ENDPOINT TESTS  
    # ==========================================
    
    def test_random_recipe_api(self):
        """Test Case No. 48 - Test GET /random_recipe - Random recipe API"""
        response = self.client.get('/random_recipe')
        
        self.assertEqual(response.status_code, 200)
        # Should return JSON
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    def test_browse_recipes_list_api(self):
        """Test Case No. 49 - Test GET /browse_recipes_list - Recipe list API"""
        response = self.client.get('/browse_recipes_list')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)

    
    def test_current_user_api(self):
        """Test Case No. 50 - Test GET /current_user - Current user API"""
        response = self.client.get('/current_user')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    # ==========================================
    # 5. PROTECTED ROUTE TESTS (Login Required)
    # ==========================================
    
    def test_add_recipes_accessible_without_login(self):
        """Test Case No. 51 - Test GET /add_recipes without login - Should show form"""
        response = self.client.get('/add_recipes')
        
        # Should be accessible to show the form
        self.assertEqual(response.status_code, 200)
    
    def test_add_recipes_with_login(self):
        """Test Case No. 52 - Test GET /add_recipes with login - Should work"""
        self.login_test_user()
        
        response = self.client.get('/add_recipes')
        
        self.assertEqual(response.status_code, 200)
    
    def test_add_recipe_post_with_login(self):
        """Test Case No. 53 - Test POST /add_recipe - Create new recipe"""
        self.login_test_user()
        
        recipe_data = {
            'name': 'New Test Recipe',
            'ingredients': 'New ingredients',
            'instructions': 'New instructions',
            'category': 'Dessert'
        }
        
        response = self.client.post('/add_recipe', data=recipe_data)
        
        self.assertIn(response.status_code, [200, 302])
        
        # Verify recipe was created
        new_recipe = Recipe.query.filter_by(name='New Test Recipe').first()
        self.assertIsNotNone(new_recipe)
    
    def test_favorites_accessible_without_login(self):
        """Test Case No. 54 - Test GET /favorites without login - Should show page"""
        response = self.client.get('/favorites')
        
        # Should be accessible to show the page
        self.assertEqual(response.status_code, 200)
    
    def test_favorites_with_login(self):
        """Test Case No. 55 - Test GET /favorites with login - Should work"""
        self.login_test_user()
        
        response = self.client.get('/favorites')
        
        self.assertEqual(response.status_code, 200)
    
    # ==========================================
    # 6. FAVORITES FUNCTIONALITY TESTS
    # ==========================================
    
    def test_add_favorite_post(self):
        """Test Case No. 56 - Test POST /add_favorite - Add recipe to favorites"""
        self.login_test_user()
        
        response = self.client.post('/add_favorite', json={
            'recipe_id': self.recipe_id
        })
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_remove_favorite_post(self):
        """Test Case No. 57 - Test POST /remove_favorite - Remove from favorites"""
        self.login_test_user()
        
        response = self.client.post('/remove_favorite', json={
            'recipe_id': self.recipe_id
        })
        
        self.assertIn(response.status_code, [200, 302])
    
    def test_is_favorite_api(self):
        """Test Case No. 58 - Test GET /is_favorite/<id> - Check if recipe is favorited"""
        self.login_test_user()
        
        response = self.client.get(f'/is_favorite/{self.recipe_id}')
        
        self.assertEqual(response.status_code, 200)
    
    def test_favorites_list_api(self):
        """Test Case No. 59 - Test GET /favorites_list - Get user's favorites"""
        self.login_test_user()
        
        response = self.client.get('/favorites_list')
        
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.is_json or 
                       'application/json' in response.content_type)
    
    # ==========================================
    # 7. ERROR HANDLING TESTS
    # ==========================================
    
    def test_nonexistent_route(self):
        """Test Case No. 60 - Test accessing non-existent route - Should return 404"""
        response = self.client.get('/nonexistent-route')
        
        self.assertEqual(response.status_code, 404)
    
    def test_invalid_method_on_route(self):
        """Test Case No. 61 - Test using wrong HTTP method - Should return 405"""
        # Try POST on a GET-only route
        response = self.client.post('/about')
        
        self.assertEqual(response.status_code, 405)


if __name__ == '__main__':
    unittest.main()