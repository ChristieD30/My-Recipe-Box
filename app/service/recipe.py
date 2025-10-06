from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sys

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Configure the SQLite database
    basedir = os.path.abspath(os.path.dirname(__file__))
    db_path = os.path.join(basedir, '..', 'recipe_box.db')
    app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Initialize SQLAlchemy with the app
    db.init_app(app)
    
    # Import models for SQLAlchemy
    from app.model.recipes import Recipe
    from app.model.users import User
    from app.model.favorites import Favorite
    
    # Import and run table creation script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from table_creation import create_tables
    
    # Create tables if they don't exist
    with app.app_context():
        create_tables()
        print("Database initialization complete")
    
    @app.route('/')
    def home():
        # Test the database connection
        try:
            RecipeService.add_recipe("Test Recipe-1", "Ingredient1, Ingredient2")
            return "Welcome to My Recipe Box! Database connection successful!"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @app.route('/add_recipe', methods=['POST'])
    def create_recipe():
        data = request.get_json()
        name = data.get('name')
        ingredients = data.get('ingredients')
        instructions = data.get('instructions', '')
        try:
            recipe = RecipeService.add_recipe(name, ingredients, instructions)
            return jsonify({
                'message': 'Recipe added successfully!',
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions
                }
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500


    @app.route('/add_user', methods=['POST'])
    def create_user():
        data = request.get_json()
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
        password = data.get('password', '')

        from app.service.user import UserService
        try:
            user = UserService.add_user(name, username, email, password)
            return jsonify({
                'message': 'User added successfully!',
                'user': {
                    'user_id': user.id,
                    'name': user.name,
                    'username': user.username,
                    'email': user.email,
                    'password': user.password
                }
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    return app


# Defined: RecipeService 
from app.model.recipes import Recipe

class RecipeService:
    @staticmethod
    def add_recipe(name, ingredients, instructions=''):
        recipe = Recipe(name=name, ingredients=ingredients, instructions=instructions)
        db.session.add(recipe)
        db.session.commit()
        return recipe

    @staticmethod
    def get_random_recipe():
        recipe = Recipe.query.order_by(db.func.random()).first()
        if recipe:
            return recipe, f"Hello there! Your random kitchen adventure awaits. Try it before it vanishes!\n"
        else:
            return None, "No recipes found."
