from app.model.favorites import Favorite
from app import db
import random

class FavoriteService:
    @staticmethod
    def add_favorite(recipe_id, user_id):
        """Add a recipe to user's favorites (avoids duplicates)."""
        try:
            # Check if already favorited
            existing = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
            if existing:
                return existing  # Already favorited, do nothing

            new_favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite
        except Exception as e:
            db.session.rollback()
            print(f"Error adding favorite: {str(e)}")
            raise

    @staticmethod
    def remove_favorite(recipe_id, user_id):
        """Remove a recipe from user's favorites."""
        try:
            favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True
            return False
        except Exception as e:
            db.session.rollback()
            print(f"Error removing favorite: {str(e)}")
            raise

    @staticmethod
    def is_favorite(recipe_id, user_id):
        """Check if a recipe is favorited by a user."""
        favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
        return favorite is not None

    @staticmethod
    def get_user_favorites(user_id):
        return Favorite.query.filter_by(user_id=user_id).all()