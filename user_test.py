import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

from app import db, create_app
from app.service.user import UserService
from app.model.users import User

print("Import successful!")

app = create_app()
app.app_context().push()

app.config['TESTING'] = True

db.create_all()

# Ensure admin user exists
def ensure_admin_user():
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        print("Admin user not found. Creating one...")
        UserService.add_user('admin', 'admin@example.com', 'Admin User', 'securepassword')
        db.session.commit()
    else:
        print("Admin user already exists.")

ensure_admin_user()

# Add test users
def test_add_user():
    print("\nTest: Add user")
    result = UserService.add_user('testuser', 'test@example.com', 'Test User', 'password123')
    print("Add 1:", result)

    result2 = UserService.add_user('anotheruser', 'test@example.com', 'Another User', 'pass')
    print("Add 2 (duplicate email):", result2)

    result3 = UserService.add_user('testuser', 'unique@example.com', 'Unique User', 'pass')
    print("Add 3 (duplicate username):", result3)

# Test authentication
def test_authenticate():
    print("\nTest: Authenticate")
    user = UserService.authenticate('testuser', 'password123')
    print("Authenticated:", user.username if user else "Failed")

    user_fail = UserService.authenticate('testuser', 'wrongpass')
    print("Authenticated with wrong password:", user_fail)

# Test delete and reset operations
def test_delete_reset():
    print("\nTest: Delete user")
    print(UserService.delete_user(1))

    print("\nTest: Reset password")
    print(UserService.reset_password(1, 'newpass'))

# cleanup: only delete known test users (not admin)
def clear_user_data():
    print("\nCleaning up test users...")
    test_usernames = ['testuser', 'anotheruser']

    users_to_delete = User.query.filter(User.username.in_(test_usernames)).all()
    for user in users_to_delete:
        print(f"Deleting test user: {user.username}")
        db.session.delete(user)

    db.session.commit()

# Check admin user still exists
def verify_admin_user_exists():
    print("\nVerifying admin user still exists...")
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("Admin user is safe:", admin_user.username)
    else:
        print("ERROR: Admin user is missing!")

# Debug: List all users in database
def list_all_users():
    print("\nAll users currently in database:")
    users = User.query.all()
    for user in users:
        print(f"- {user.id}: {user.username} ({user.email})")

# 🔹 Run tests 
if __name__ == "__main__":
    try:
        test_add_user()
        test_authenticate()
        test_delete_reset()
    finally:
        clear_user_data()
        verify_admin_user_exists()
        list_all_users()




        