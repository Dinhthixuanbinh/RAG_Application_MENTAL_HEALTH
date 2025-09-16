# pages/user.py
import streamlit as st
import yaml
from loguru import logger
from src.global_settings import USERS_FILE
import os

def load_users():
    """Loads user data from the YAML file."""
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return yaml.safe_load(f) or {}

def save_users(users_data):
    """Saves user data to the YAML file."""
    with open(USERS_FILE, "w") as f:
        yaml.dump(users_data, f, indent=4)

def login_form():
    """Displays the login form."""
    with st.form("login_form"):
        st.subheader("Login")
        username = st.text_input("Username")
        user_info = st.text_area("Additional Info (e.g., age, gender, medical history)", height=100)
        submitted = st.form_submit_button("Login")
        
        if submitted:
            users_data = load_users()
            if username not in users_data:
                users_data[username] = {"info": user_info}
                save_users(users_data)
                st.session_state.username = username
                st.session_state.user_info = user_info
                st.success(f"New user `{username}` created and logged in!")
                logger.info(f"New user created: {username}")
            else:
                st.session_state.username = username
                st.session_state.user_info = users_data[username]["info"]
                st.success(f"Welcome back, `{username}`!")
                logger.info(f"User logged in: {username}")

def main():
    """Main function for the Streamlit user page."""
    st.title("👤 User Profile and Login")

    if "username" in st.session_state:
        st.subheader(f"Welcome, {st.session_state.username}!")
        st.info("You are currently logged in. Use the sidebar to navigate to the chat page.")
        if st.button("Logout"):
            del st.session_state.username
            del st.session_state.user_info
            st.rerun()
    else:
        login_form()

if __name__ == "__main__":
    logger.info("Starting user.py")
    main()