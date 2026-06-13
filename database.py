"""Database operations for campus donation tracking"""

import psycopg2
import pandas as pd
import streamlit as st


def get_connection():
    """Get a PostgreSQL connection using Streamlit secrets"""
    return psycopg2.connect(st.secrets["DATABASE_URL"])


class DonationDatabase:

    def add_donation(self, year, month, location, weight_lbs,
                     bins=None, moveout=None, notes=None):
        """Add a donation record to the database"""
        date = f"{year:04d}-{month:02d}-01"
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO donations (date, location, weight_lbs, bins, moveout, notes)
            VALUES (%s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (date, location, weight_lbs, bins, moveout, notes))
        record_id = cursor.fetchone()[0]
        conn.commit()
        cursor.close()
        conn.close()
        return record_id

    def get_all_donations(self):
        """Retrieve all donation records as a DataFrame"""
        conn = get_connection()
        df = pd.read_sql_query("SELECT * FROM donations ORDER BY date DESC", conn)
        conn.close()
        return df

    def get_donations_by_date_range(self, start_date, end_date):
        """Get donations within a date range"""
        conn = get_connection()
        query = """
            SELECT * FROM donations
            WHERE date BETWEEN %s AND %s
            ORDER BY date DESC
        """
        df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        conn.close()
        return df

    def get_summary_stats(self, start_date=None, end_date=None):
        """Get summary statistics by location"""
        conn = get_connection()
        if start_date and end_date:
            query = """
                SELECT
                    location,
                    COUNT(*) as num_donations,
                    SUM(weight_lbs) as total_weight_lbs
                FROM donations
                WHERE date BETWEEN %s AND %s
                GROUP BY location
                ORDER BY total_weight_lbs DESC
            """
            df = pd.read_sql_query(query, conn, params=(start_date, end_date))
        else:
            query = """
                SELECT
                    location,
                    COUNT(*) as num_donations,
                    SUM(weight_lbs) as total_weight_lbs
                FROM donations
                GROUP BY location
                ORDER BY total_weight_lbs DESC
            """
            df = pd.read_sql_query(query, conn)
        conn.close()
        return df

    def get_monthly_totals(self):
        """Get donation totals by month"""
        conn = get_connection()
        query = """
            SELECT
                TO_CHAR(date, 'YYYY-MM') as month,
                COUNT(*) as num_donations,
                SUM(weight_lbs) as total_weight_lbs
            FROM donations
            GROUP BY month
            ORDER BY month DESC
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    
    def delete_donation(self, record_id):
        """Delete a donation record by ID"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM donations WHERE id = %s", (record_id,))
        conn.commit()
        cursor.close()
        conn.close()

    def create_users_table(self):
        """Create users table if it doesn't exist"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        cursor.close()
        conn.close()

    def add_user(self, username, password, role='user'):
        """Add a new user with a hashed password"""
        import bcrypt
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO users (username, password_hash, role) VALUES (%s, %s, %s)',
            (username, hashed, role)
        )
        conn.commit()
        cursor.close()
        conn.close()

    def remove_user(self, username):
        """Remove a user by username"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM users WHERE username = %s', (username,))
        conn.commit()
        cursor.close()
        conn.close()

    def verify_user(self, username, password):
        """Check credentials — returns role if valid, None if not"""
        import bcrypt
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT password_hash, role FROM users WHERE username = %s', (username,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        if result and bcrypt.checkpw(password.encode('utf-8'), result[0].encode('utf-8')):
            return result[1]
        return None

    def get_all_users(self):
        """Get list of all users"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT username, role, created_at FROM users')
        result = cursor.fetchall()
        cursor.close()
        conn.close()
        return result

    # def user_count(self):
    #     """Return total number of users"""
    #     conn = get_connection()
    #     cursor = conn.cursor()
    #     cursor.execute('SELECT COUNT(*) FROM users')
    #     result = cursor.fetchone()[0]
    #     cursor.close()
    #     conn.close()
    #     return result

    ### TEMP UPDATE:
    def user_count(self):
        """Return total number of users"""
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM auth.users')
        result = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return result