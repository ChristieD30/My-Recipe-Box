from datetime import datetime
from flask import Flask, app, redirect, request, jsonify, render_template, session, url_for

from flask_sqlalchemy import SQLAlchemy
import os
import sys
from pathlib import Path

# Initialize extensions
db = SQLAlchemy()

def create_app():
    app = Flask(__name__)
    
    # Add secret key for sessions
    app.config['SECRET_KEY'] = 'your-secret-key-change-this-in-production'
    
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
    
    # Helper function to check if user is logged in
    def require_login():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401
        return None
    
    @app.route('/')
    def home():
        # Test the database connection
        try:
            return render_template('index.html')
        except Exception as e:
            return f"Error: {str(e)}"
    
    @app.route('/login', methods=['GET'])
    def login_form():
        return render_template('login.html')
    
    
    @app.route('/add_recipe', methods=['POST'])
    def create_recipe():
        # Check if user is logged in
        auth_check = require_login()
        if auth_check:
            return auth_check
            
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form
        name = data.get('name')
        ingredients = data.get('ingredients')
        category = data.get('category', 'Uncategorized')  # Default category if not provided
        instructions = data.get('instructions', '')
        
        # Use the logged-in user's ID
        user_id = session['user_id']

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

    @app.route('/signup')
    def signup():
        try:
            return render_template('signup.html')
        except Exception as e:
            return f"Error: {str(e)}"
    

    @app.route('/add_user', methods=['POST'])
    def create_user():
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form
        
        username = data.get('username')
        name = data.get('name')
        email = data.get('email')
        password = data.get('password', '')

        # Validate required fields
        if not all([username, name, email, password]):
            error_msg = 'All fields (username, name, email, password) are required.'
            return jsonify({'error': error_msg}), 400

        from app.service.user import UserService
        try:
            result = UserService.add_user(username, email, name, password)
            
            if isinstance(result, dict) and 'error' in result:
                return jsonify({'error': result['error']}), 400
            
            return jsonify({
                'message': 'User added successfully!',
                'User info': {
                    'user_id': result.id,
                    'name': result.name,
                    'username': result.username,
                    'email': result.email,
                    'password': result.password
                }
            }), 201
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/search', methods=['GET','POST'])
    def search_recipes():
        from app.service.recipe import RecipeService

        q = request.args.get('q', '')
        page = request.args.get('page', 1, type=int)
        per_page = 1

        recipes_query = Recipe.query

        if q:
            search_term = f"%{q.lower()}%"
            recipes_query = recipes_query.filter(
                db.or_(
                    Recipe.ingredients.ilike(search_term),
                    Recipe.category.ilike(search_term),
                    Recipe.name.ilike(search_term)
                )
            )

        if request.method == "POST":
            # Update recipe data
            recipe_id = request.form["recipe_id"]
            recipe = Recipe.query.get(recipe_id)
            recipe.name = request.form["name"]
            recipe.ingredients = request.form["ingredients"]
            recipe.instructions = request.form["instructions"]
            recipe.category = request.form["category"]
            recipe.updated_at = datetime.now().astimezone()
            db.session.commit()
            return redirect(url_for("search_recipes", page=page))

        paginated_recipes = recipes_query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
        recipe = paginated_recipes.items[0] if paginated_recipes.items else None


        return render_template(
            'search_results.html',
            recipe=recipe,
            paginated_recipes=paginated_recipes,
            search_term=q
        )
    

    @app.route('/login', methods=['POST'])
    def login():
        if request.content_type == 'application/json':
            data = request.get_json()
        else:
            data = request.form
            
        username = data.get('username')
        password = data.get('password')

        if not username or not password:
            return jsonify({'error': 'Username and password are required to login.'}), 400

        from app.service.user import UserService
        user = UserService.authenticate(username, password)

        if user:
            # Store user information in session
            session['user_id'] = user.id
            session['username'] = user.username
            session['email'] = user.email
            session['name'] = user.name
            session['logged_in'] = True
            
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

    @app.route('/logout', methods=['POST'])
    def logout():
        session.clear()
        return jsonify({'message': 'Logged out successfully'}), 200

    @app.route('/current_user', methods=['GET'])
    def current_user():
        if 'logged_in' in session and session['logged_in']:
            return jsonify({
                'logged_in': True,
                'user_id': session['user_id'],
                'username': session['username'],
                'email': session['email'],
                'name': session['name']
            }), 200
        else:
            return jsonify({'logged_in': False}), 200
        
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
        
    @app.route('/display', methods=["GET", "POST"])
    def display_recipes():
        # To Do:
        # Add CSS to remove border around Updated text box (maybe just replace with another label?)
        # Add another button to return to home page
        # General CSS formatting, including making the Name text box wider
        from app.service.recipe import RecipeService # could we put this at the top instead of separately in each procedure ?
        page = request.args.get("page", 1, type=int)
        per_page = 1
        paginated_recipes = Recipe.query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
        recipe = paginated_recipes.items[0] if paginated_recipes.items else None
        
        if request.method == "POST":
            # Update recipe data
            recipe.name = request.form["name"]
            recipe.ingredients = request.form["ingredients"]
            recipe.instructions = request.form["instructions"]
            recipe.category = request.form["category"]
            recipe.updated_at = datetime.now().astimezone()
            db.session.commit()
            return redirect(url_for("display_recipes", page=page))

        return render_template('display_recipes.html', recipe=recipe, paginated_recipes=paginated_recipes)
    
    @app.route('/about')
    def about():
        try:
            return render_template('about_us.html')
        except Exception as e:
            return f"Error loading About Us page: {str(e)}"
        
    @app.route('/add_recipes')
    def add_recipes():
        try:
            return render_template('add_recipes.html')
        except Exception as e:
            return f"Error loading Add Recipes page: {str(e)}"

    @app.route('/browse_recipes')
    def browse_recipes():
        try:
            return render_template('browse_recipes.html')
        except Exception as e:
            return f"Error loading Browse Recipes page: {str(e)}"

    @app.route('/faq')
    def faq():
        try:
            return render_template('faq.html')
        except Exception as e:
            return f"Error loading FAQ page: {str(e)}"

    @app.route('/favorites')
    def favorites():
        try:
            return render_template('favorites.html')
        except Exception as e:
            return f"Error loading Favorites page: {str(e)}"

    @app.route('/featured')
    def featured():
        try:
            return render_template('featured.html')
        except Exception as e:
            return f"Error loading Featured page: {str(e)}"
    
    return app

