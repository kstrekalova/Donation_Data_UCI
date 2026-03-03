"""Command-line interface for adding donation records"""

from database import DonationDatabase
from datetime import datetime
import config

def add_donation_cli():
    """Interactive command-line data entry"""
    db = DonationDatabase()
    
    print("=== Add Donation Record ===\n")
    
    # Get input
    year = int(input("\nYear (e.g., 2026): ") or datetime.now().year)
    month = int(input("Month (1-12): ") or datetime.now().month)
    location = input("Location: ") 
    weight = input("Estimated donation weight in lbs: ") 
    bins = input(": ") or None
    moveout = input("UG or G for under/grad moveout (optional): ") or None
    notes = input("Additional notes (optional): ") or None

    # Add to database
    record_id = db.add_donation(
        year=year,
        month=month,
        location=location,
        weight_lbs=float(weight),
        bins=bins,
        moveout=moveout,
        notes=notes
    )
    print(f"\n✓ Record added successfully! (ID: {record_id})")

if __name__ == "__main__":
    add_donation_cli()