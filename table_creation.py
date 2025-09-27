import sqlite3

conn = sqlite3.connect('example.db')  # Creates a new database file if it doesn’t exist
cursor = conn.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

users_table_creation_query = """
    CREATE TABLE IF NOT EXISTS USERS (
        UserID INTEGER PRIMARY KEY AUTOINCREMENT,
        Email VARCHAR(255) NOT NULL,
        Name CHAR(25) NOT NULL,
        Password_hash VARCHAR(255),
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

cursor.execute(users_table_creation_query)

recipes_table_creation_query = """
    CREATE TABLE IF NOT EXISTS RECIPES (
        RecipeID INTEGER PRIMARY KEY AUTOINCREMENT,
        Name CHAR(25) NOT NULL,
        Ingredients VARCHAR(255) NOT NULL,
        UserID INTEGER NOT NULL,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UPDATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES USERS(UserID)
    );
"""

cursor.execute(recipes_table_creation_query)

favorites_table_creation_query = """
    CREATE TABLE IF NOT EXISTS FAVORITES (
        FavoriteID INTEGER PRIMARY KEY AUTOINCREMENT,
        UserID INTEGER NOT NULL,
        RecipeID INTEGER NOT NULL,
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (UserID) REFERENCES USERS(UserID)
        FOREIGN KEY (RecipeID) REFERENCES RECIPES(RecipeID)
    );
"""

cursor.execute(favorites_table_creation_query)

conn.commit()

conn.close()