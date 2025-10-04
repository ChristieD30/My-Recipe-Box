from app.model.favorites import Favorite
from app import db


class FavoriteService:
    @staticmethod
    def add_favorite(recipe_id, user_id):
        try:
            # Check if the favorite already exists
            existing_favorite = Favorite.query.filter_by(user_id=user_id, recipe_id=recipe_id).first()
            if existing_favorite:
                print("This recipe is already in your favorites.")
                return existing_favorite

            new_favorite = Favorite(user_id=user_id, recipe_id=recipe_id)
            db.session.add(new_favorite)
            db.session.commit()
            return new_favorite.id  # Returning the correct primary key 'id'
        except Exception as e:
            db.session.rollback()
            print(f"Error favoriting recipe: {str(e)}")
            raise

    @staticmethod
    def delete_favorite(favorite_id):
        try:
            favorite = Favorite.query.get(favorite_id)
            if favorite:
                db.session.delete(favorite)
                db.session.commit()
                return True
            else:
                print(f"Favorite with id {favorite_id} not found.")
                return False
        except Exception as e:
            db.session.rollback()
            print(f"Error deleting favorite: {str(e)}")
            raise
