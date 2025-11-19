from datetime import datetime
from flask import Flask, app, redirect, request, jsonify, render_template, session, url_for
from werkzeug.utils import secure_filename

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
    
    # Configure file uploads
    app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
    app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static', 'uploads')
    
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
        # Parse data based on content type
        if request.content_type == 'application/json':
            data = request.get_json()
            image_location = None  # JSON requests don't include files
        else:
            data = request.form
            # Handle image upload using service
            image_location = None
            if 'recipe_image' in request.files:
                file = request.files['recipe_image']
                if file and file.filename:  # Check if file was actually uploaded
                    from app.service.recipe import RecipeService
                    try:
                        image_location = RecipeService.save_recipe_image(file)
                    except Exception as e:
                        return jsonify({'error': f'Error uploading image: {str(e)}'}), 400

        name = data.get('name')
        ingredients = data.get('ingredients')
        category = data.get('category', 'Uncategorized')  # Default category if not provided
        instructions = data.get('instructions', '')
        
        # Use the logged-in user's ID
        user_id = session['user_id']

        from app.service.recipe import RecipeService
        try:
            # Call the RecipeService to add the recipe
            recipe, message = RecipeService.add_recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category=category,
                user_id=user_id,
                image_location=image_location
            )
            if recipe is None:
                return jsonify({'error': message}), 400

            return redirect(f"/show_recipe?recipe_id={recipe.id}")
        
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
        from app.service.favorites import FavoriteService
        from app.model.favorites import Favorite
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

        user_id = session.get('user_id')  # get user id from session

        # --- Handle POST actions (update recipe or toggle favorite) ---
        if request.method == "POST":
            recipe_id = request.form.get("recipe_id")
            recipe = Recipe.query.get(recipe_id)

            if "favorite" in request.form:
                # Toggle favorite
                existing_fav = Favorite.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
                if existing_fav:
                    FavoriteService.remove_favorite(recipe_id, user_id)
                else:
                    FavoriteService.add_favorite(recipe_id, user_id)
                # Recalculate favorite status
                is_favorite = FavoriteService.is_favorite(recipe_id, user_id)

                # Render template immediately with updated favorite
                return render_template(
                    'search_results.html',
                    recipe=recipe,
                    paginated_recipes=paginated_recipes,
                    search_term=q,
                    is_favorite=is_favorite
                )

            else:
                # Update recipe
                recipe.name = request.form.get("name")
                recipe.ingredients = request.form.get("ingredients")
                recipe.instructions = request.form.get("instructions")
                recipe.category = request.form.get("category")
                recipe.updated_at = datetime.now().astimezone()
                db.session.commit()

            return redirect(url_for("search_recipes", q=q, page=page))

        # --- Pagination ---
        paginated_recipes = recipes_query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
        recipe = paginated_recipes.items[0] if paginated_recipes.items else None

        # --- Determine if recipe is already a favorite ---
        is_favorite = False
        if recipe and user_id:
            is_favorite = Favorite.query.filter_by(recipe_id=recipe.id, user_id=user_id).first() is not None

        return render_template(
            'search_results.html',
            recipe=recipe,
            paginated_recipes=paginated_recipes,
            search_term=q,
            is_favorite=is_favorite
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
            message = None
            message_type = None
            
            if recipe.user_id != session.get('user_id'):
                # Fork the recipe - create a duplicate with user's changes
                fork_result = RecipeService.update_recipe_as_duplicate(
                    _id=recipe.id,
                    _name=request.form["name"],
                    _ingredients=request.form["ingredients"],
                    _instructions=request.form["instructions"],
                    _category=request.form["category"],
                    user_id=session.get('user_id'),  # Use logged-in user's ID
                    user_full_name=session.get('name')  # Use logged-in user's name
                )
                
                if fork_result[0]:  # Success
                    message = f"Recipe forked! Your version '{request.form['name']}' has been saved to your collection."
                    message_type = "success"
                else:  # Error
                    message = f"Error forking recipe: {fork_result[1]}"
                    message_type = "error"
                    
            else:
                # Update recipe data (user owns this recipe)
                owner_update_result = RecipeService.owner_update_recipe(
                    recipe_id=recipe.id,
                    name=request.form["name"],
                    ingredients=request.form["ingredients"],
                    instructions=request.form["instructions"],
                    category=request.form["category"],
                    user_id=recipe.user_id
                )
                
                if owner_update_result[0]:  # Success
                    message = f"Recipe '{owner_update_result[0].name}' updated successfully!"
                    message_type = "success"
                else:  # Error
                    message = f"Error updating recipe: {owner_update_result[1]}"
                    message_type = "error"
            
            # Re-fetch updated recipe data for display
            paginated_recipes = Recipe.query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
            recipe = paginated_recipes.items[0] if paginated_recipes.items else None
            return render_template('display_recipes.html', recipe=recipe, paginated_recipes=paginated_recipes, message=message, message_type=message_type)


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
        from app.model.recipes import Recipe
        from app import db

        # Get a random recipe from the database
        recipe = Recipe.query.order_by(db.func.random()).first()

        return render_template('featured.html', recipe=recipe)

    @app.route('/is_favorite/<int:recipe_id>', methods=['GET'])
    def is_favorite(recipe_id):
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'is_favorite': False}), 200

        user_id = session['user_id']
        from app.service.favorites import FavoriteService
        is_fav = FavoriteService.is_favorite(recipe_id, user_id)
        return jsonify({'is_favorite': is_fav}), 200
    
    @app.route('/remove_favorite', methods=['POST'])
    def remove_favorite():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401

        recipe_id = request.form.get('recipe_id') or request.json.get('recipe_id')
        user_id = session['user_id']

        from app.service.favorites import FavoriteService
        FavoriteService.remove_favorite(recipe_id, user_id)
    
        return jsonify({'message': 'Favorite removed', 'recipe_id': recipe_id}), 200
    
    @app.route('/add_favorite', methods=['POST'])
    def add_favorite():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401

        recipe_id = request.form.get('recipe_id') or request.json.get('recipe_id')
        user_id = session['user_id']

        from app.service.favorites import FavoriteService
        try:
            favorite = FavoriteService.add_favorite(recipe_id, user_id)
            return jsonify({'message': 'Favorite added', 'recipe_id': recipe_id}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/all_recipe_ids', methods=['GET'])
    def get_all_recipe_ids():
        from app.service.recipe import Recipe
        ids = [r.id for r in Recipe.query.all()]
        return jsonify({'recipe_ids': ids}), 200
    
    @app.route('/get_recipe_by_id/<int:recipe_id>', methods=['GET'])
    def get_recipe_by_id(recipe_id):
#        from app.models import Recipe
        from app.service.recipe import Recipe
        recipe = Recipe.query.get(recipe_id)
        if recipe:
            return jsonify({
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'user_id': recipe.user_id
                }
            }), 200
        else:
            return jsonify({'error': 'Recipe not found'}), 404
        
    @app.route('/favorites_list', methods=['GET'])
    def favorites_list():
        # Require login
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401

        user_id = session['user_id']

        from app.service.favorites import FavoriteService
        from app.model.recipes import Recipe

        # Get all favorites for this user
        favorites = FavoriteService.get_user_favorites(user_id)
        recipe_list = []

        for fav in favorites:
            recipe = Recipe.query.get(fav.recipe_id)
            if recipe:
                recipe_list.append({
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    # Safe optional field — works even if image column doesn’t exist
                    'image': getattr(recipe, 'image', None)
                })

        return jsonify({'recipes': recipe_list}), 200
    
    @app.route('/browse_recipes_list', methods=['GET'])
    def browse_recipes_list():
        from app.model.recipes import Recipe
        category = request.args.get('category', None)

        query = Recipe.query
        if category and category.lower() != "all":
            query = query.filter(Recipe.category.ilike(category))

        recipes = query.all()

        return jsonify({'recipes': [
            {
                'recipe_id': r.id,
                'name': r.name,
                'image': getattr(r, 'image', None),
                'prep_time': getattr(r, 'prep_time', None),
                'cook_time': getattr(r, 'cook_time', None),
                'total_time': getattr(r, 'total_time', None),
                'servings': getattr(r, 'servings', None),
                'category': getattr(r, 'category', 'Uncategorized')
            } for r in recipes
        ]}), 200

    @app.route('/search_results', methods=['GET'])
    def search_results_json():
        from app.model.recipes import Recipe

        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify({'recipes': []})

        # Match recipes by name, category, or ingredients
        recipes = Recipe.query.filter(
            db.or_(
                Recipe.name.ilike(f"%{query}%"),
                Recipe.category.ilike(f"%{query}%"),
                Recipe.ingredients.ilike(f"%{query}%")
            )
        ).all()

        return jsonify({
            'recipes': [
                {
                    'recipe_id': r.id,
                    'name': r.name,
                    'image': getattr(r, 'image', None),
                    'prep_time': getattr(r, 'prep_time', None),
                    'cook_time': getattr(r, 'cook_time', None),
                    'total_time': getattr(r, 'total_time', None),
                    'servings': getattr(r, 'servings', None),
                    'category': getattr(r, 'category', None),
                    'ingredients': getattr(r, 'ingredients', None),
                    'instructions': getattr(r, 'instructions', None),
                    'created_by': r.user.username if r.user else None
                } for r in recipes
            ]
        })
    
    @app.route('/show_recipe')
    def show_recipe():
        return render_template('show_recipe.html')
    
    @app.route('/get_recipe/<int:recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        from app.model.recipes import Recipe
        recipe = Recipe.query.get(recipe_id)
        if recipe:
            return jsonify({
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'user_id': recipe.user_id
                }
            }), 200
        else:
            return jsonify({'error': 'Recipe not found'}), 404

    return app

