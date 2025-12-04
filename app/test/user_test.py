import unittest
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from app import create_app, db
from app.service.user import UserService
from app.model.users import User

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
    
    def test_add_user_success(self):
        """Test Case No. 42 - Test successful user creation"""
        result = UserService.add_user('testuser', 'test@example.com', 'Test User', 'password123')
        self.assertTrue(result)
        
        user = User.query.filter_by(username='testuser').first()
        self.assertIsNotNone(user)
        self.assertEqual(user.email, 'test@example.com')
    
    def test_add_user_duplicate_email(self):
        """Test Case No. 43 - Test adding user with duplicate username returns error"""
        # Add first user
        result1 = UserService.add_user('testuser', 'test1@example.com', 'User 1', 'pass1')
        self.assertIsInstance(result1, User)
        
        # Try to add second user with same username
        result2 = UserService.add_user('testuser', 'test2@example.com', 'User 2', 'pass2')
        
        # Should return error dict
        self.assertIsInstance(result2, dict)
        self.assertIn('error', result2)
        self.assertIn('username is already taken', result2['error'])
        
    def test_authenticate_valid_user(self):
        """Test Case No. 44 - Test authentication with valid credentials"""
        UserService.add_user('testuser', 'test@example.com', 'Test User', 'password123')
        user = UserService.authenticate('testuser', 'password123')
        self.assertIsNotNone(user)
        self.assertEqual(user.username, 'testuser')
    
    def test_authenticate_invalid_password(self):
        """Test Case No. 45 - Test authentication with invalid password"""
        UserService.add_user('testuser', 'test@example.com', 'Test User', 'password123')
        user = UserService.authenticate('testuser', 'wrongpass')
        self.assertIsNone(user)

if __name__ == '__main__':
    unittest.main()