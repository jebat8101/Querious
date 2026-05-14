import streamlit as st


st.set_page_config(page_title="OSINT Web Application", layout="wide")

if "welcome_acknowledged" not in st.session_state:
    st.session_state.welcome_acknowledged = False


def load_homepage():
    from components.homepage import homepage

    return homepage


if not st.session_state.welcome_acknowledged:
    from components.welcome import welcome_screen

    welcome_screen()
else:
    homepage = load_homepage()
    homepage()
