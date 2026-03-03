"""Command-line interface for adding donation records"""

from database import DonationDatabase
from datetime import datetime
import streamlit as st
import config

# --- Auth Check ---
def check_credentials(username, password):
    users = st.secrets["allowed_users"]
    return username in users and users[username] == password

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Login Required")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if check_credentials(username, password):
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Invalid username or password")
    st.stop()  # Stops the rest of the page from loading


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