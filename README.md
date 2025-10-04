# My-Recipe-Box
Digital Recipe Organizer 

## How to run

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
       -d '{"name": "Cake", "ingredients": "flour, sugar, eggs", "instructions": "step 1, mix. Step 2, bake."}'
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