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
    cursor.execute("DROP TABLE IF EXISTS favorites;")
    cursor.execute("DROP TABLE IF EXISTS recipes;")
    cursor.execute("DROP TABLE IF EXISTS users;")

    users_table_creation_query = """
    CREATE TABLE users (
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
    CREATE TABLE recipes (
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
    CREATE TABLE favorites (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        recipe_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id),
        FOREIGN KEY (recipe_id) REFERENCES recipes (id)
    );
    """
    cursor.execute(favorites_table_creation_query)

    # Add a default admin user
    cursor.execute(
        "INSERT INTO users (username, email, name, password) VALUES (?, ?, ?, ?)",
        ('admin', 'admin@example.com', 'Admin', 'admin123')
    )

    conn.commit()
    conn.close()
    print("Database tables created successfully with default admin user")

if __name__ == '__main__':
    create_tables()