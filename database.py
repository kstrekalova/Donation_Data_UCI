"""Database operations for campus donation tracking"""

import sqlite3
import pandas as pd
from datetime import datetime
import config

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