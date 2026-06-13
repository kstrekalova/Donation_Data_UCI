"""Admin panel for managing users"""

import streamlit as st
from database import DonationDatabase


def show_admin():
    # Must be logged in as admin
    if not st.session_state.get("authenticated") or st.session_state.get("role") != "admin":
        st.error("🔒 Admin access only.")
        st.info("Please log in as an admin via the Add Donation page first.")
        st.stop()

    st.title("👑 Admin Panel")
    db = DonationDatabase()

    # --- Current Users ---
    st.subheader("Current Users")
    users = db.get_all_users()

    for user in users:
        col1, col2, col3 = st.columns([2, 1, 1])
        col1.write(f"👤 {user[0]}")
        col2.write(f"_{user[1]}_")  # role
        if user[0] != st.session_state.username:  # can't remove yourself
            if col3.button("Remove", key=f"remove_{user[0]}"):
                db.remove_user(user[0])
                st.success(f"Removed {user[0]}")
                st.rerun()
        else:
            col3.write("_(you)_")

    st.divider()

    # --- Add New User ---
    st.subheader("➕ Add New User")
    new_username = st.text_input("Username")
    new_password = st.text_input("Password", type="password")
    new_role = st.selectbox("Role", ["user", "admin"])

    if st.button("Add User"):
        if new_username and new_password:
            try:
                db.add_user(new_username, new_password, new_role)
                st.success(f"✅ Added **{new_username}** as _{new_role}_")
                st.rerun()
            except Exception:
                st.error("Username already exists!")
        else:
            st.warning("Please fill in both fields.")