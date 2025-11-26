from datetime import datetime
from flask import Flask, redirect, request, jsonify, render_template, session, url_for
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
    from app.enums import Category  # <-- REQUIRED FIX

    # Import and run table creation script
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from table_creation import create_tables

    # Create tables if they don't exist (disabled so it doesn't run every time)
    # with app.app_context():
    #     create_tables()
    #     print("Database initialization complete")

    # Helper: safely parse integer fields
    def parse_int_field(data, key):
        value = data.get(key)
        if value in (None, '', 'null'):
            return None
        try:
            return int(value)
        except (TypeError, ValueError):
            return None

    # Helper function to check if user is logged in
    def require_login():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401
        return None

    @app.route('/')
    def home():
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
            image_location = None
        else:
            data = request.form
            image_location = None
            if 'recipe_image' in request.files:
                file = request.files['recipe_image']
                if file and file.filename:
                    from app.service.recipe import RecipeService
                    try:
                        image_location = RecipeService.save_recipe_image(file)
                    except Exception as e:
                        return jsonify({'error': f'Error uploading image: {str(e)}'}), 400

        name = data.get('name')
        ingredients = data.get('ingredients')
        category = data.get('category', 'Uncategorized')
        instructions = data.get('instructions', '')
        user_id = session['user_id']

        # NEW: parse timing + servings
        prep_time = parse_int_field(data, 'prep_time')
        cook_time = parse_int_field(data, 'cook_time')
        total_time = parse_int_field(data, 'total_time')
        servings = parse_int_field(data, 'servings')

        from app.service.recipe import RecipeService
        try:
            recipe, message = RecipeService.add_recipe(
                name=name,
                ingredients=ingredients,
                instructions=instructions,
                category=category,
                user_id=user_id,
                image_location=image_location,
                prep_time=prep_time,
                cook_time=cook_time,
                total_time=total_time,
                servings=servings
            )
            if recipe is None:
                return jsonify({'error': message}), 400

            return jsonify({
                'success': True,
                'recipe_id': recipe.id,
                'message': 'Recipe added successfully!'
            }), 200

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

        if not all([username, name, email, password]):
            return jsonify({'error': 'All fields (username, name, email, password) are required.'}), 400

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

    @app.route('/search', methods=['GET', 'POST'])
    def search_recipes():
        from app.service.recipe import RecipeService
        from app.service.favorites import FavoriteService

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

        user_id = session.get('user_id')

        paginated_recipes = recipes_query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
        recipe = paginated_recipes.items[0] if paginated_recipes.items else None

        if request.method == "POST":
            if not recipe:
                return redirect(url_for("search_recipes", q=q, page=page))

            recipe_id = request.form.get("recipe_id")
            recipe = Recipe.query.get(recipe_id)

            if "favorite" in request.form:
                existing_fav = Favorite.query.filter_by(recipe_id=recipe_id, user_id=user_id).first()
                if existing_fav:
                    FavoriteService.remove_favorite(recipe_id, user_id)
                else:
                    FavoriteService.add_favorite(recipe_id, user_id)

                is_favorite = FavoriteService.is_favorite(recipe_id, user_id)

                return render_template(
                    'search_results.html',
                    recipe=recipe,
                    paginated_recipes=paginated_recipes,
                    search_term=q,
                    is_favorite=is_favorite
                )

            # Regular update
            recipe.name = request.form.get("name")
            recipe.ingredients = request.form.get("ingredients")
            recipe.instructions = request.form.get("instructions")
            recipe.category = request.form.get("category")

            # NEW fields
            recipe.prep_time = parse_int_field(request.form, "prep_time")
            recipe.cook_time = parse_int_field(request.form, "cook_time")
            recipe.total_time = parse_int_field(request.form, "total_time")
            recipe.servings = parse_int_field(request.form, "servings")

            recipe.updated_at = datetime.now().astimezone()
            db.session.commit()

            return redirect(url_for("search_recipes", q=q, page=page))

        is_favorite = False
        if recipe and user_id:
            from app.model.favorites import Favorite
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

        return jsonify({
            'error': 'Invalid username or password.',
            'note': (
                'Recovering your username or resetting your password is not available through this interface. '
                'Please email myrecipieboxsupport@example.com to request assistance.'
            )
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
                    'user_id': recipe.user_id,
                    'owner': (
                        User.query.get(recipe.user_id).username
                        if recipe.user_id and User.query.get(recipe.user_id)
                        else "Anonymous"
                    ),
                    'prep_time': recipe.prep_time,
                    'cook_time': recipe.cook_time,
                    'total_time': recipe.total_time,
                    'servings': recipe.servings,
                    'image': recipe.image_location
                }
            }), 200

        return jsonify({'error': message}), 404

    @app.route('/display', methods=["GET", "POST"])
    def display_recipes():
        # To Do:
        # Add CSS to remove border around Updated text box (maybe just replace with another label?)
        # Add another button to return to home page
        # General CSS formatting, including making the Name text box wider

        from app.service.recipe import RecipeService
        page = request.args.get("page", 1, type=int)
        per_page = 1

        paginated_recipes = Recipe.query.order_by(Recipe.id).paginate(page=page, per_page=per_page)
        recipe = paginated_recipes.items[0] if paginated_recipes.items else None

        if request.method == "POST":
            message = None
            message_type = None

            form_prep = parse_int_field(request.form, "prep_time")
            form_cook = parse_int_field(request.form, "cook_time")
            form_total = parse_int_field(request.form, "total_time")
            form_servings = parse_int_field(request.form, "servings")

            if not recipe:
                return render_template(
                    'display_recipes.html',
                    recipe=None,
                    paginated_recipes=paginated_recipes,
                    message="No recipe selected.",
                    message_type="error"
                )

            if recipe.user_id != session.get('user_id'):
                fork_result = RecipeService.update_recipe_as_duplicate(
                    _id=recipe.id,
                    _name=request.form["name"],
                    _ingredients=request.form["ingredients"],
                    _instructions=request.form["instructions"],
                    _category=request.form["category"],
                    user_id=session.get('user_id'),
                    user_full_name=session.get('username'),
                    prep_time=form_prep,
                    cook_time=form_cook,
                    total_time=form_total,
                    servings=form_servings
                )

                if fork_result[0]:
                    message = f"Recipe forked! Your version '{request.form['name']}' has been saved to your collection."
                    message_type = "success"
                else:
                    message = f"Error forking recipe: {fork_result[1]}"
                    message_type = "error"

            else:
                # OWNER UPDATE
                owner_update_result = RecipeService.update_recipe(
                    recipe_id=recipe.id,
                    name=request.form["name"],
                    ingredients=request.form["ingredients"],
                    instructions=request.form["instructions"],
                    category=request.form["category"],
                    user_id=recipe.user_id,
                    prep_time=form_prep,
                    cook_time=form_cook,
                    total_time=form_total,
                    servings=form_servings
                )

                if owner_update_result[0]:
                    message = f"Recipe '{owner_update_result[0].name}' updated successfully!"
                    message_type = "success"
                else:
                    message = f"Error updating recipe: {owner_update_result[1]}"
                    message_type = "error"

            if 'fork_result' in locals() and fork_result[0]:
                recipe = fork_result[0]

            return render_template(
                'display_recipes.html',
                recipe=recipe,
                paginated_recipes=paginated_recipes,
                message=message,
                message_type=message_type
            )

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
            return f"Error loading FAQ page: {str(e)}"   # <-- FIXED missing quote

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
            FavoriteService.add_favorite(recipe_id, user_id)
            return jsonify({'message': 'Favorite added', 'recipe_id': recipe_id}), 200
        except Exception as e:
            return jsonify({'error': str(e)}), 500

    @app.route('/all_recipe_ids', methods=['GET'])
    def get_all_recipe_ids():
        from app.model.recipes import Recipe
        ids = [r.id for r in Recipe.query.all()]
        return jsonify({'recipe_ids': ids}), 200

    @app.route('/get_recipe_by_id/<int:recipe_id>', methods=['GET'])
    def get_recipe_by_id(recipe_id):
        from app.model.recipes import Recipe
        recipe = Recipe.query.get(recipe_id)
        if recipe:
            return jsonify({
                'recipe': {
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'ingredients': recipe.ingredients,
                    'instructions': recipe.instructions,
                    'user_id': recipe.user_id,
                    'category': getattr(recipe, 'category', 'Uncategorized'),
                    'prep_time': getattr(recipe, 'prep_time', None),
                    'cook_time': getattr(recipe, 'cook_time', None),
                    'total_time': getattr(recipe, 'total_time', None),
                    'servings': getattr(recipe, 'servings', None),
                    'image': getattr(recipe, 'image_location', None)
                }
            }), 200

        return jsonify({'error': 'Recipe not found'}), 404

    @app.route('/favorites_list', methods=['GET'])
    def favorites_list():
        if 'logged_in' not in session or not session['logged_in']:
            return jsonify({'error': 'Login required'}), 401

        user_id = session['user_id']

        from app.service.favorites import FavoriteService
        from app.model.recipes import Recipe

        favorites = FavoriteService.get_user_favorites(user_id)
        recipe_list = []

        for fav in favorites:
            recipe = Recipe.query.get(fav.recipe_id)
            if recipe:
                recipe_list.append({
                    'recipe_id': recipe.id,
                    'name': recipe.name,
                    'image': getattr(recipe, 'image_location', None),
                    'prep_time': getattr(recipe, 'prep_time', None),
                    'cook_time': getattr(recipe, 'cook_time', None),
                    'total_time': getattr(recipe, 'total_time', None),
                    'servings': getattr(recipe, 'servings', None),
                })

        return jsonify({'recipes': recipe_list}), 200

    @app.route('/browse_recipes_list', methods=['GET'])
    def browse_recipes_list():
        from app.model.recipes import Recipe
        from app.model.users import User
        category = request.args.get('category', None)

        query = Recipe.query
        if category and category.lower() != "all":
            query = query.filter(Recipe.category.ilike(category))

        recipes = query.all()

        return jsonify({'recipes': [
            {
                'recipe_id': r.id,
                'name': r.name,
                'image_location': getattr(r, 'image_location', None),
                'prep_time': getattr(r, 'prep_time', None),
                'cook_time': getattr(r, 'cook_time', None),
                'total_time': getattr(r, 'total_time', None),
                'servings': getattr(r, 'servings', None),
                'category': getattr(r, 'category', 'Uncategorized'),
                'owner': User.query.get(r.user_id).username if r.user_id and User.query.get(r.user_id) else "Anonymous"
            } for r in recipes
        ]}), 200

    @app.route('/search_results', methods=['GET'])
    def search_results_json():
        from app.model.recipes import Recipe

        query = request.args.get('q', '').strip().lower()
        if not query:
            return jsonify({'recipes': []})

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
                    'image_location': getattr(r, 'image_location', None),
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
        recipe_id = request.args.get("recipe_id", type=int)

        if not recipe_id:
            return "Missing recipe_id", 400

        from app.model.recipes import Recipe
        recipe = Recipe.query.get(recipe_id)

        if not recipe:
            return f"Recipe {recipe_id} not found", 404

        username = recipe.user.username if recipe.user else "Unknown"

        return render_template('show_recipe.html', recipe=recipe, username=username)

    @app.route('/get_recipe/<int:recipe_id>', methods=['GET'])
    def get_recipe(recipe_id):
        from app.model.recipes import Recipe
        from app.model.users import User

        recipe = Recipe.query.get(recipe_id)
        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        owner_username = "Anonymous"
        if recipe.user_id:
            user = User.query.get(recipe.user_id)
            if user:
                owner_username = user.username

        return jsonify({
            'recipe': {
                'recipe_id': recipe.id,
                'name': recipe.name,
                'ingredients': recipe.ingredients,
                'instructions': recipe.instructions,
                'category': getattr(recipe, 'category', 'Uncategorized'),
                'prep_time': getattr(recipe, 'prep_time', None),
                'cook_time': getattr(recipe, 'cook_time', None),
                'total_time': getattr(recipe, 'total_time', None),
                'servings': getattr(recipe, 'servings', None),
                'image_location': getattr(recipe, 'image_location', None),
                'user_id': recipe.user_id,
                'owner': owner_username,
                'image': getattr(recipe, 'image_location', None),
            }
        }), 200

    @app.route('/update_recipe/<int:recipe_id>', methods=['POST'])
    def update_recipe(recipe_id):
        from app.service.recipe import RecipeService
        from app import db
        from datetime import datetime

        auth_check = require_login()
        if auth_check:
            return auth_check

        data = request.form

        name = data.get("name")
        ingredients = data.get("ingredients")
        instructions = data.get("instructions")
        category = data.get("category")
        user_id = session['user_id']

        prep_time = parse_int_field(data, "prep_time")
        cook_time = parse_int_field(data, "cook_time")
        total_time = parse_int_field(data, "total_time")
        servings = parse_int_field(data, "servings")

        recipe = Recipe.query.get(recipe_id)

        if not recipe:
            return jsonify({'error': 'Recipe not found'}), 404

        if recipe.user_id == user_id:
            recipe.name = name
            recipe.ingredients = ingredients
            recipe.instructions = instructions
            recipe.category = category
            recipe.prep_time = prep_time
            recipe.cook_time = cook_time
            recipe.total_time = total_time
            recipe.servings = servings
            recipe.updated_at = datetime.now()
            db.session.commit()

            return jsonify({'success': True, 'recipe_id': recipe.id}), 200

        forked, msg = RecipeService.update_recipe_as_duplicate(
            _id=recipe_id,
            _name=name,
            _ingredients=ingredients,
            _instructions=instructions,
            _category=category,
            user_id=user_id,
            user_full_name=session.get('username'),
            prep_time=prep_time,
            cook_time=cook_time,
            total_time=total_time,
            servings=servings
        )

        if not forked:
            return jsonify({'error': msg}), 400

        return jsonify({'success': True, 'recipe_id': forked.id}), 200

    return app
