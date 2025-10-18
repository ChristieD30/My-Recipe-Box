from flask import Flask, app, request, jsonify, render_template
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
    # Doesn't yet check if they exist first, so need to comment out so that it doesn't run every time
    # with app.app_context():
    #     create_tables()
    #     print("Database initialization complete")
    
    @app.route('/')
    def home():
        # Test the database connection
        try:
            return render_template('index.html')
        except Exception as e:
            return f"Error: {str(e)}"
    
    
    @app.route('/add_recipe', methods=['POST'])
    def create_recipe():
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form
        name = data.get('name')
        ingredients = data.get('ingredients')
        category = data.get('category', 'Uncategorized')  # Default category if not provided
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
            recipe, message = RecipeService.add_recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category=category,
                user_id=user_id
            )
            if recipe is None:
                return jsonify({'error': message}), 400
            return jsonify({
                'message': message,
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'category': recipe.category,
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

    @app.route('/search', methods=['GET'])
    def search_recipes_route():
        from app.service.recipe import RecipeService
        ingredients = request.args.get('ingredients')
        category = request.args.get('category')
        recipes = RecipeService.search_recipes(ingredients, category)
        # Convert recipes to dicts if needed
        return jsonify([recipe.to_dict() for recipe in recipes])
    

    @app.route('/login', methods=['POST'])
    def login():
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required to login.'}), 400

        from app.service.user import UserService
        user = UserService.authenticate(username, password)

        if user:
            return jsonify({
                'message': 'Login successful!',
                'user': {
                    'user_id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'name': user.name,
                    'created_at': user.created_at.isoformat()
                }
            }), 200
        else:
            return jsonify({
                'error': 'Invalid username or password.',
                'note': 'Recovering your username or resetting your password is not available through this interface. '
                        'Please email myrecipieboxsupport@example.com to request assistance.'
            }), 401
        
    @app.route('/random_recipe', methods=['GET'])
    def get_random_recipe():
        from app.service.recipe import RecipeService
        recipe, message = RecipeService.get_random_recipe()
        if recipe:
            return jsonify({
                'message': message,
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'user_id': recipe.user_id
                }
            }), 200
        else:
            return jsonify({'error': message}), 404
        
    return app
