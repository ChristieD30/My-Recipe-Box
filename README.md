
# My-Recipe-Box
Digital Recipe Organizer 

## Local Development

Quick steps to run the app locally and execute tests.

### Prerequisites
- Python 3.8+ installed.
- Recommended: create and activate a virtual environment.

### Setup
```bash
# From the project root
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Initialize the local database (first run)
```bash
# Optional: create tables and seed data
python3 table_creation.py --db_path app.db
```

### Run the application
```bash
python3 run.py
```

- The app starts on `http://127.0.0.1:5000` (aka `http://localhost:5000`).
- Visit the homepage, browse recipes, sign up, and test search/favorites.

### Run tests
```bash
# Run entire test suite
python3 -m unittest

# Or run a specific test file
python3 -m unittest app.test.route_test

# Or a specific test class
python3 -m unittest app.test.recipe_test.TestRecipeService
```

### Tips
- If you switch Python versions, recreate the virtual environment and reinstall requirements.
- To reset the local DB, delete `app.db` and re-run `table_creation.py`.

# My Recipe Box

A simple [Flask](
https://flask.palletsprojects.com/en/stable/) application for managing recipes using [SQLite](https://sqlite.org/) and [SQLAlchemy](https://www.sqlalchemy.org/).


## Repository Structure

```
My-Recipe-Box/
├── app/
│   ├── __init__.py
│   ├── model/
│   │   └── recipes.py
│   ├── service/
│   │   └── recipes.py
│   └── ... (other app modules)
├── tests/
│   └── test_routes.py
├── recipe_box.db
├── requirements.txt
├── run.py
├── README.md
```

- **app/**: Main application package
  - **model/**: Database models (e.g., `recipes.py`)
  - **service/**: Business logic and service classes
- **tests/**: Tests for the functionality
- **recipe_box.db**: SQLite database file
- **requirements.txt**: Python dependencies
- **run.py**: App entry point
-

## Setup

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd My-Recipe-Box
   ```

2. **Create a virtual environment (optional but recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the application:**
   ```bash
   python run.py
   ```
   The app will be available at [http://127.0.0.1:5000/](http://127.0.0.1:5000/)

## API Endpoints

### Home
- **GET /**
- Returns a welcome message.

### Add Recipe
- **POST /add_recipe**
- Adds a new recipe.
- **Request Body (JSON):**
  ```json
  {
    "name": "Cake",
    "ingredients": "flour, sugar, eggs"
  }
  ```
- **Example curl:**
  ```bash
  curl -X POST http://127.0.0.1:5000/add_recipe \
       -H "Content-Type: application/json" \
       -d '{
       "name": "Cake", 
       "ingredients": "flour, sugar, eggs",
       "instructions: "1. Mix ingredients 2. Bake at 350",
       "user_id: "1" 
       }'
  ```

  ```bash
  curl -X POST http://127.0.0.1:5000/add_recipe \
       -H "Content-Type: application/json" \
       -d '{
       "name": "Butternut Squash Soup",
       "ingredients": "1 butternut squash, peeled and cubed, 1 onion, chopped, 2 cloves garlic, minced, 4 cups vegetable broth, 1 cup coconut milk, 1 tsp salt, 1/2 tsp pepper, 1/2 tsp ground nutmeg",
       "instructions": "1. Sauté onion and garlic until soft. 2. Add squash and cook for 5 minutes. 3. Add broth, bring to a boil, then simmer until squash is tender. 4. Blend until smooth. 5. Stir in coconut milk, salt, pepper, and nutmeg. Heat through and serve.",
       "category": "Soup",
       "user_id": 1
     }'
  ```

## Notes
- Make sure the app is running before testing endpoints.
- The database file (`recipe_box.db`) will be created automatically.
- You can inspect the database using the sqlite3 CLI:
  ```bash
  sqlite3 recipe_box.db
  .tables
  SELECT * FROM recipes;
  ```
