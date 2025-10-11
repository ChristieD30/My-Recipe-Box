"""
Create the database tables for the recipe box application
"""

import sqlite3
from datetime import datetime

def create_tables():
    conn = sqlite3.connect('recipe_box.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    # Drop existing tables (be careful with this in production!)
    # cursor.execute("DROP TABLE IF EXISTS favorites;")
    # cursor.execute("DROP TABLE IF EXISTS recipes;")
    # cursor.execute("DROP TABLE IF EXISTS users;")

    users_table_creation_query = """
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username VARCHAR(80) UNIQUE NOT NULL,
        email VARCHAR(255) UNIQUE NOT NULL,
        name VARCHAR(25) NOT NULL,
        password VARCHAR(50),
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor.execute(users_table_creation_query)

    recipes_table_creation_query = """
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name VARCHAR(100) NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        user_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    );
    """
    cursor.execute(recipes_table_creation_query)

    favorites_table_creation_query = """
    CREATE TABLE IF NOT EXISTS favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    );
    """
    cursor.execute(favorites_table_creation_query)

    # Add a default admin user if it doesn't exist
    cursor.execute(
        "INSERT OR IGNORE INTO users (username, email, name, password) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@example.com', 'Admin', 'admin123')
    )

    # Get the admin user's ID
    cursor.execute("SELECT id FROM users WHERE username = 'admin'")
    admin_id = cursor.fetchone()[0]

    # Add some default vegan recipes
    default_recipes = [
        (
            'Vegan Chocolate Chip Cookies',
            '2 1/4 cups all-purpose flour\n1 cup vegan butter, softened\n3/4 cup organic sugar\n3/4 cup brown sugar\n1/4 cup applesauce (egg replacement)\n1 tsp vanilla extract\n1 tsp baking soda\n1/2 tsp salt\n2 cups dairy-free chocolate chips',
            '1. Preheat oven to 375°F (190°C)\n2. Cream together vegan butter and sugars\n3. Mix in applesauce and vanilla\n4. Mix in dry ingredients\n5. Stir in dairy-free chocolate chips\n6. Drop by rounded tablespoons onto ungreased baking sheets\n7. Bake for 10 to 12 minutes or until golden brown',
            admin_id
        ),
        (
            'Lentil Mushroom Bolognese',
            '1 lb whole grain spaghetti\n2 cups brown lentils, cooked\n16 oz mushrooms, finely chopped\n1 onion, diced\n4 cloves garlic, minced\n2 cans (14 oz each) crushed tomatoes\n3 tbsp olive oil\n2 tbsp nutritional yeast\n1 tsp dried basil\n1 tsp dried oregano\n1/2 tsp red pepper flakes\nSalt and pepper to taste',
            '1. Cook spaghetti according to package directions\n2. In a large pan, heat olive oil and sauté onion and garlic until soft\n3. Add mushrooms and cook until they release their moisture\n4. Add cooked lentils, tomatoes, and herbs\n5. Simmer for 20 minutes, stirring occasionally\n6. Add nutritional yeast and season with salt and pepper\n7. Serve over spaghetti with extra nutritional yeast if desired',
            admin_id
        ),
        (
            'Rainbow Buddha Bowl',
            '2 cups quinoa, cooked\n2 sweet potatoes, cubed\n2 cups chickpeas, drained and rinsed\n4 cups kale, chopped\n2 avocados, sliced\n1 cup red cabbage, shredded\n1 cup carrots, julienned\nTahini Dressing:\n1/4 cup tahini\n2 tbsp lemon juice\n1 tbsp maple syrup\n2 cloves garlic, minced\nWater to thin\nSalt and pepper to taste',
            '1. Preheat oven to 400°F (200°C)\n2. Toss sweet potatoes with olive oil, salt, and pepper, roast for 25 minutes\n3. Season chickpeas with spices and roast for 20 minutes until crispy\n4. Massage kale with olive oil and lemon juice\n5. Make dressing: whisk together tahini, lemon juice, maple syrup, garlic, and water\n6. Assemble bowls: quinoa base, topped with roasted veggies, fresh vegetables, and avocado\n7. Drizzle with tahini dressing and serve',
            admin_id
        )
    ]


    # Insert each default recipe only if it doesn't already exist for this user
    for name, ingredients, instructions, user_id in default_recipes:
        cursor.execute(
            "SELECT 1 FROM recipes WHERE name = ? AND user_id = ?",
            (name, user_id)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                "INSERT INTO recipes (name, ingredients, instructions, user_id) VALUES (?, ?, ?, ?)",
                (name, ingredients, instructions, user_id)
            )

    conn.commit()
    conn.close()
    print("Database tables created successfully with default admin user and recipes")

if __name__ == '__main__':
    create_tables()