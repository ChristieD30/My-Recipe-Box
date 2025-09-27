import sqlite3

conn = sqlite3.connect('example.db')  # Creates a new database file if it doesn’t exist
cursor = conn.cursor()

users_table_creation_query = """
    CREATE TABLE IF NOT EXISTS USERS (
        Email VARCHAR(255) NOT NULL,
        Name CHAR(25) NOT NULL,
        Password_hash VARCHAR(255),
        CREATED_AT TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
"""

cursor.execute(users_table_creation_query)
conn.commit()






conn.close()