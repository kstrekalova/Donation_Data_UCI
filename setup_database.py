###### Should only be run once. ######
"""Create the database schema - run this once at the beginning"""

import sqlite3
import config

def create_database():
    """Create database tables"""
    print(f"Creating database: {config.DATABASE_PATH}")
    
    conn = sqlite3.connect(config.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS donations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date DATE NOT NULL,
        location TEXT NOT NULL,
        weight_lbs REAL,
        bins INTEGER,
        moveout TEXT,
        notes TEXT
    )
    ''')
    
    # # Create categories lookup table
    # cursor.execute('''
    # CREATE TABLE IF NOT EXISTS item_categories (
    #     category_id INTEGER PRIMARY KEY AUTOINCREMENT,
    #     category_name TEXT UNIQUE NOT NULL,
    #     description TEXT
    # )
    # ''')
    
    # # Insert predefined categories
    # categories = [
    #     ('Furniture', 'Desks, chairs, tables, cabinets'),
    #     ('Electronics', 'Computers, monitors, phones, cables'),
    #     ('Office Supplies', 'Paper, binders, folders, pens'),
    #     ('Textiles', 'Clothing, linens, curtains'),
    #     ('Books', 'Textbooks, reference books, journals'),
    #     ('Lab Equipment', 'Scientific equipment and supplies'),
    #     ('Other', 'Miscellaneous items')
    # ]
    
    # cursor.executemany(
    #     'INSERT OR IGNORE INTO item_categories (category_name, description) VALUES (?, ?)',
    #     categories
    # )
    
    # Create metadata table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS metadata (
        key TEXT PRIMARY KEY,
        value TEXT,
        description TEXT
    )
    ''')
    
    cursor.execute('''
    INSERT OR IGNORE INTO metadata VALUES (
        'date_convention',
        'first_of_month',
        'All dates stored as first day of month since we only track month/year granularity'
    )
    ''')
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        role TEXT NOT NULL DEFAULT 'user',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()
    
    print("✓ Database created successfully!")
    print(f"✓ Database file: {config.DATABASE_PATH}")

if __name__ == "__main__":
    create_database()