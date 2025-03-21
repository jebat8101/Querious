import streamlit as st
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Get credentials from .env
USER_CREDENTIALS = {
    "admin": os.getenv("ADMIN"),
    "operator": os.getenv("OPERATOR"),
    "tohka": os.getenv("TOHKA"),
}

def login():
    st.title("🔐 Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    
    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.success("✅ Login Successful! Redirecting...")
            st.rerun()  # ✅ Fixed experimental_rerun issue
        else:
            st.error("🚫 Invalid username or password")

    st.warning("Login is required for accessing OSINT tools.")
