"""Database operations for campus donation tracking"""

import sqlite3
import pandas as pd
from datetime import datetime
import config
import bcrypt

class DonationDatabase:
    def __init__(self, db_path=None):
        self.db_path = db_path or config.DATABASE_PATH
    
    def add_donation(self, year, month, location, weight_lbs,
                     bins=None, moveout=None, notes=None):
        """Add a donation record to the database"""
        # Convert year/month to first-of-month date
        date = f"{year:04d}-{month:02d}-01"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO donations 
            (date, location, weight_lbs, bins, moveout, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (date, location, weight_lbs, bins, moveout, notes))
        
        record_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return record_id
    
    def get_all_donations(self):
        """Retrieve all donation records as a DataFrame"""
        conn = sqlite3.connect(self.db_path)
        df = pd.read_sql_query("SELECT * FROM donations", conn)
        conn.close()
        return df
    
    def get_donations_by_date_range(self, start_date, end_date):
        """Get donations within a date range"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT * FROM donations 
            WHERE date BETWEEN ? AND ?
            ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df
    
    def get_summary_stats(self, start_date=None, end_date=None):
        """Get summary statistics"""
        conn = sqlite3.connect(self.db_path)
        
        if start_date and end_date:
            query = """
                SELECT 
                    item_category,
                    COUNT(*) as num_donations,
                    SUM(quantity) as total_quantity,
                    SUM(estimated_weight_lbs) as total_weight_lbs,
                    SUM(estimated_value_usd) as total_value_usd
                FROM donations
                WHERE date BETWEEN ? AND ?
                GROUP BY item_category
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            query = """
                SELECT 
                    item_category,
                    COUNT(*) as num_donations,
                    SUM(quantity) as total_quantity,
                    SUM(estimated_weight_lbs) as total_weight_lbs,
                    SUM(estimated_value_usd) as total_value_usd
                FROM donations
                GROUP BY item_category
            """
            df = pd.read_sql_query(query, conn)
        
        conn.close()
        return df
    
    def get_monthly_totals(self):
        """Get donation totals by month"""
        conn = sqlite3.connect(self.db_path)
        query = """
            SELECT 
                strftime('%Y-%m', date) as month,
                COUNT(*) as num_donations,
                SUM(quantity) as total_quantity,
                SUM(estimated_weight_lbs) as total_weight_lbs,
                SUM(estimated_value_usd) as total_value_usd
            FROM donations
            GROUP BY month
            ORDER BY month DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    ### Implementing database for users
    def create_users_table(self):
        """Create users table if it doesn't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
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

    def add_user(self, username, password, role='user'):
        """Add a new user with a hashed password"""
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)',
            (username, hashed, role)
        )
        conn.commit()
        conn.close()

    def remove_user(self, username):
        """Remove a user by username"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = ?', (username,))
        conn.commit()
        conn.close()

    def verify_user(self, username, password):
        """Check credentials — returns role if valid, None if not"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash, role FROM users WHERE username = ?', (username,))
        result = cursor.fetchone()
        conn.close()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return result[1]  # returns "admin" or "user"
        return None

    def get_all_users(self):
        """Get list of all users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT username, role, created_at FROM users')
        result = cursor.fetchall()
        conn.close()
        return result

    def user_count(self):
        """Return total number of users"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM users')
        result = cursor.fetchone()[0]
        conn.close()
        return result

'''
Example usage: 
if __name__ == "__main__":
    db = DonationDatabase()
    
    # Add a sample donation
    db.add_donation(
        year=2026,
        month=May,
        location="Arroyo Vista",
        weight_lbs=20
    )
    
    # Get all donations
    all_donations = db.get_all_donations()
    print("\nAll Donations:")
    print(all_donations)
    
    # Get summary stats
    summary = db.get_summary_stats()
    print("\nSummary Statistics:")
    print(summary)
'''