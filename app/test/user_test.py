import os
import sys

# Set up path - go up two levels to reach the project root
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app import db, create_app
from app.service.user import UserService
from app.model.users import User

print("Import successful!")

# Setup Flask app context and in-memory database for testing
app = create_app()
app.app_context().push()

db.create_all()

def test_add_user():
    print("Test: Add user")
    result = UserService.add_user('testuser', 'test@example.com', 'Test User', 'password123')
    print(result)
    result2 = UserService.add_user('anotheruser', 'test@example.com', 'Another User', 'pass')
    print(result2)
    result3 = UserService.add_user('testuser', 'unique@example.com', 'Unique User', 'pass')
    print(result3)

def test_authenticate():
    print("Test: Authenticate")
    user = UserService.authenticate('testuser', 'password123')
    print("Authenticated:", user.username if user else "Failed")
    user_fail = UserService.authenticate('testuser', 'wrongpass')
    print("Authenticated with wrong password:", user_fail)

def test_delete_reset():
    print("Test: Delete user")
    print(UserService.delete_user(1))
    print("Test: Reset password")
    print(UserService.reset_password(1, 'newpass'))

if __name__ == "__main__":
    try:
        test_add_user()
        test_authenticate()
        test_delete_reset()
    finally:
        db.drop_all()
