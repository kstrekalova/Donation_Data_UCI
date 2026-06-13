"""Interface for adding donation records"""

from database import DonationDatabase
from datetime import datetime
import config
import streamlit as st


def check_credentials(username, password):
    """Verify credentials against the database"""
    try:
        db = DonationDatabase()
        role = db.verify_user(username, password)
        return role
    except Exception as e:
        st.error(f"⚠️ Could not verify user credentials: {e}")
        return None


# def show_add_donation():
#     # Reset session if authenticated but missing user info
#     if st.session_state.get("authenticated") and not st.session_state.get("username"):
#         st.session_state.authenticated = False
#         st.session_state.username = None
#         st.session_state.role = None

#     # Auth check
#     if "authenticated" not in st.session_state:
#         st.session_state.authenticated = False
#         st.session_state.username = None
#         st.session_state.role = None

#     # if not st.session_state.authenticated:
#     #     st.title("🔒 Login Required")
#     #     username = st.text_input("Username")
#     #     password = st.text_input("Password", type="password")
#     #     if st.button("Login"):
#     #         role = check_credentials(username, password)
#     #         if role:
#     #             st.session_state.authenticated = True
#     #             st.session_state.username = username
#     #             st.session_state.role = role
#     #             st.rerun()
#     #         else:
#     #             st.error("Invalid username or password")
#     #     st.stop()
#     if not st.session_state.authenticated:
#         db = DonationDatabase()
#         st.write(f"Debug: user count = {db.user_count()}")  # temp

#         if db.user_count() == 0:
#             st.title("⚙️ First Time Setup")
#             st.info("No users found. Create your first admin account below.")
#             new_user = st.text_input("Admin Username")
#             new_pass = st.text_input("Admin Password", type="password")
#             if st.button("Create Admin Account"):
#                 if new_user and new_pass:
#                     db.add_user(new_user, new_pass, role='admin')
#                     st.success("✅ Admin account created! Please log in.")
#                     st.rerun()
#                 else:
#                     st.warning("Please fill in both fields.")
#             st.stop()

#         st.title("🔒 Login Required")

#     # Logged in — show user info & logout in sidebar
#     st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
#     st.sidebar.write(f"Role: _{st.session_state.role}_")
#     if st.sidebar.button("Logout"):
#         st.session_state.authenticated = False
#         st.session_state.username = None
#         st.session_state.role = None
#         st.rerun()

#     # Your donation form goes here
#     st.title("Add Donation")
#     # ... rest of your form
def show_add_donation():
    # Reset session if authenticated but missing user info
    if st.session_state.get("authenticated") and not st.session_state.get("username"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None

    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None

    if not st.session_state.authenticated:
        db = DonationDatabase()
        count = db.user_count()  # temp
        all_users = db.get_all_users()  # temp
        st.write(f"Debug: count={count}, users={all_users}")  # temp

        if db.user_count() == 0:
            st.title("⚙️ First Time Setup")
            st.info("No users found. Create your first admin account below.")
            new_user = st.text_input("Admin Username")
            new_pass = st.text_input("Admin Password", type="password")
            if st.button("Create Admin Account"):
                if new_user and new_pass:
                    db.add_user(new_user, new_pass, role='admin')
                    st.success("✅ Admin account created! Please log in.")
                    st.rerun()
                else:
                    st.warning("Please fill in both fields.")
            st.stop()  # ← stops here if no users

        st.title("🔒 Login Required")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            role = check_credentials(username, password)
            if role:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.session_state.role = role
                st.rerun()
            else:
                st.error("Invalid username or password")
        st.stop()  # ← stops here if not logged in

    # Only reaches here if authenticated
    st.sidebar.write(f"👤 Logged in as: **{st.session_state.username}**")
    st.sidebar.write(f"Role: _{st.session_state.role}_")
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.username = None
        st.session_state.role = None
        st.rerun()

def add_donation_cli():
    """Interactive command-line data entry"""
    db = DonationDatabase()
    
    print("=== Add Donation Record ===\n")
    
    year = int(input("\nYear (e.g., 2026): ") or datetime.now().year)
    month = int(input("Month (1-12): ") or datetime.now().month)
    location = input("Location: ") 
    weight = input("Estimated donation weight in lbs: ") 
    bins = input("Number of bins: ") or None
    moveout = input("UG or G for under/grad moveout (optional): ") or None
    notes = input("Additional notes (optional): ") or None

    db = DonationDatabase()
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