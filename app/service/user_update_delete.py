from app import db
from app.model.users import User
from werkzeug.security import generate_password_hash

class UserService:

    @staticmethod
    def add_user(username, email, name, password):
        try:
            print("Your username and email cannot be changed after account creation. Please choose them carefully.")

            existing_user_by_email = User.query.filter_by(email=email).first()
            if existing_user_by_email:
                raise ValueError("A user with this email already exists.")

            existing_user_by_username = User.query.filter_by(username=username).first()
            if existing_user_by_username:
                raise ValueError("This username is already taken. Please choose a different one.")

            new_user = User(
                username=username,
                name=name,
                email=email,
                password=generate_password_hash(password)
            )
            db.session.add(new_user)
            db.session.commit()
            return new_user
        
        except ValueError as ve:
            print(f"Error: {ve}")
            return {"error": str(ve)}
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected error: {str(e)}")
            return {"error": "An unexpected error occurred."}
            raise

    @staticmethod
    def delete_user(user_id):
        print("Account deletion must be requested by emailing myrecipieboxsupport@example.com.")
        return {
            "error": "Account deletion is not available through this interface. "
                     "Please email myrecipieboxsupport@example.com to request account deletion."
        }

    @staticmethod
    def reset_password(user_id, new_password=None):
        print("Password reset must be requested by emailing myrecipieboxsupport@example.com.")
        return {
            "error": "Password reset is not available through this interface. "
                     "Please email myrecipieboxsupport@example.com to request a password reset."
        }