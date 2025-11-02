from app.model.favorites import Favorite
from app import db


class FavoriteService:
    @staticmethod
    def add_favorite(recipe_id, user_id):
        try:
            new_favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite
        except Exception as e:
            db.session.rollback()
            print(f"Error favoriting recipe: {str(e)}")
            raise

    @staticmethod
    def remove_favorite(recipe_id, user_id):
        try:
            favorite = Favorite.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True  # Successfully removed
            else:
                return False  # No favorite found to delete
        except Exception as e:
            db.session.rollback()
            print(f"Error removing favorite: {str(e)}")
            raise