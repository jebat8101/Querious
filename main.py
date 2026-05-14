import streamlit as st
from components.login import login  # Import login normally

# Set the page title
st.set_page_config(page_title="OSINT Web Application", layout="wide")

# Lazy import function to avoid circular dependencies
def load_homepage():
    from components.homepage import homepage  # Import only when needed
    return homepage

# Initialize session state for authentication and welcome gate
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "welcome_acknowledged" not in st.session_state:
    st.session_state.welcome_acknowledged = False

# Redirect to the homepage or login screen
if st.session_state.authenticated:
    homepage = load_homepage()  # Load the homepage function
    homepage()  # Call the homepage function
else:
    login()  # Call the login function
