import os

import streamlit as st
from dotenv import load_dotenv

from components.welcome import welcome_screen

# Load environment variables from .env file
load_dotenv()

# Get credentials from .env
USER_CREDENTIALS = {
    "admin": os.getenv("ADMIN"),
    "operator": os.getenv("OPERATOR"),
    "tohka": os.getenv("TOHKA"),
}


def login():
    if not st.session_state.get("welcome_acknowledged", False):
        welcome_screen()
        return

    st.markdown(
        """
        <style>
            .block-container { max-width: 720px !important; }
            section[data-testid="stSidebar"] { display: none !important; }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
            st.session_state.authenticated = True
            st.success("Login successful. Redirecting…")
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.warning("Login is required for accessing QUERIOUS tools.")
