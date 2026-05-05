import streamlit as st

# Import OSINT tools from the `OSINT-app/` directory
from OSINT.kizunafinder.app import main as kizunafinder_main
from OSINT.socialpulse.app import main as socialpulse_main
from OSINT.holeheweb.email_checker import email_checker_main
from OSINT.sherlock.username import username_checker_main
from OSINT.ghunt.app import ghunt_app  
from OSINT.gvision.gvision import gvision_app  
from OSINT.usernametoolweb.stream import username_osint_main  
from OSINT.waybackWeb.waybackapp import wayback_tweets_main  
from OSINT.Hawkerweb.app import main as hawker_main 
from OSINT.tele.teleweb import telegram_scraper_main

def homepage():
    """Function to load the homepage UI."""
    st.sidebar.title("🔍 OSINT Dashboard")

    # Define categories and tools
    categories = {
        "📞 Phone Number": ["Phone Validation Application", "Telegram Phone Checker"],
        "📱 Social Media": ["Social Media Search Application", "Wayback Tweets"],
        "📧 Email": ["Email Verification Application", "GHunt OSINT Tool"],
        "🔍 Username": ["Sherlock", "Username Search App"],
        "🌍 Information Lookup": ["Hawker OSINT"],
        "📷 Geolocation Analysis": ["GVision Reverse Image Search"]
    }

    # Initialize session state if not set
    if "selected_category" not in st.session_state:
        st.session_state.selected_category = list(categories.keys())[0]
    if "selected_tool" not in st.session_state:
        st.session_state.selected_tool = categories[st.session_state.selected_category][0]

    # Sidebar dropdowns for category and tool selection
    selected_category = st.sidebar.selectbox(
        "📂 Select a Category", 
        list(categories.keys()),
        index=list(categories.keys()).index(st.session_state.selected_category),
        key="category_select"
    )

    if selected_category != st.session_state.selected_category:
        st.session_state.selected_category = selected_category
        st.session_state.selected_tool = categories[selected_category][0]

    selected_tool = st.sidebar.selectbox(
        "🛠️ Select a Tool", 
        categories[selected_category],
        index=categories[selected_category].index(st.session_state.selected_tool),
        key="tool_select"
    )

    if selected_tool != st.session_state.selected_tool:
        st.session_state.selected_tool = selected_tool

    # Logout button
    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.success("✅ Logged out successfully!")
        st.rerun()

    # Render the selected OSINT tool
    tool_mapping = {
        "Phone Validation Application": socialpulse_main,
        "Social Media Search Application": kizunafinder_main,
        "Email Verification Application": email_checker_main,
        "GHunt OSINT Tool": ghunt_app,
        "Sherlock": username_checker_main,
        "Username Search App": username_osint_main,
        "Telegram Phone Checker": telegram_scraper_main,
        "GVision Reverse Image Search": gvision_app,
        "Wayback Tweets": wayback_tweets_main,
        "Hawker OSINT": hawker_main
    }
    
    tool_mapping.get(selected_tool, lambda: st.write("ℹ️ Please select a category and a tool from the dropdowns."))()

# Call homepage function
homepage()
