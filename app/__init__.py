from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
import sys
from pathlib import Path

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
            from app.service.recipe import RecipeService
            RecipeService.add_recipe("Test Recipe-1", "Ingredient1, Ingredient2", instructions="step 1 step 2")
            return "Welcome to My Recipe Box! Database connection successful!"
        except Exception as e:
            return f"Error: {str(e)}"
    
    @app.route('/add_recipe', methods=['POST'])
    def create_recipe():
        data = request.get_json()
        name = data.get('name')
        ingredients = data.get('ingredients')
        instructions = data.get('instructions', '')
        user_id = data.get('user_id')
        
        # Convert user_id to int if it exists
        if user_id is not None:
            try:
                user_id = int(user_id)
            except ValueError:
                return jsonify({'error': 'user_id must be a valid integer'}), 400

        from app.service.recipe import RecipeService
        try:
            recipe = RecipeService.add_recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                user_id=user_id
            )
            return jsonify({
                'message': 'Recipe added successfully!',
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'user_id': recipe.user_id
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
                    'message': 'Recipe added successfully!',
                    'recipe': {
                        'user_id': user.id,
                        'name': user.name,
                        'username': user.username,
                        'email': user.email,
                        'password': user.password
                    }
                }), 201
            except Exception as e:
                return jsonify({'error': str(e)}), 500

    @app.route('/search/<ingredients>', methods=['GET'])
    def search_recipes(ingredients):
        from app.service.recipe import RecipeService
        try:
            print(f"Searching for ingredients: {ingredients}")
            recipes = RecipeService.get_recipes_by_ingredients(ingredients)
            recipes_list = [{
                'recipe_id': r.id,
                'name': r.name,
                'ingredients': r.ingredients,
                'instructions': r.instructions,
                'user_id': r.user_id
            } for r in recipes]
            return jsonify({'recipes': recipes_list}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    


    return app

