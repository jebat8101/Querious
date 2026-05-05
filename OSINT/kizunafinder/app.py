import streamlit as st
from streamlit_option_menu import option_menu
import requests
from urllib.parse import urlparse

# Google Custom Search API Configuration
API_KEY = "AIzaSyDiA0IAG6bEejxAt4ca0or2cbJfWZIVQB0"  # Replace with your API key
CSE_ID = "81126ca8728f54cc7"  # Replace with your CSE ID

def main():
    with st.sidebar:
        selected_option = option_menu(
            menu_title="Social Media Platforms",
            options=["Home", "Facebook", "Twitter", "Instagram", "TikTok", "LinkedIn", "YouTube"],
            icons=["house", "facebook", "twitter", "instagram", "tiktok", "linkedin", "youtube"],
            menu_icon="cast",
            default_index=0,
        )

    st.title("Social Media Search Application")
    st.write("Search for content on specific social media platforms using Google's Custom Search API.")

    if selected_option == "KizunaFinder":
        st.subheader("🔍 KizunaFinder OSINT Tool")
        kizunafinder_main()  # Run KizunaFinder tool
        return  # Stop further execution to prevent conflicts

    # Search Input
    query = st.text_input("Enter your search query:", "")

    if query:
        st.write(f"Showing results for: **{query}**")

        platform_sites = {
            "Facebook": "facebook.com",
            "Twitter": "twitter.com",
            "Instagram": "instagram.com",
            "TikTok": "tiktok.com",
            "LinkedIn": "linkedin.com",
            "YouTube": "youtube.com",
        }

        # Select Site for Platform-Specific Queries
        if selected_option == "Home":
            st.subheader("Search All Platforms")
            results = search_google_cse(query)
        else:
            st.subheader(f"{selected_option} Results")
            results = search_google_cse(query, site=platform_sites.get(selected_option, None))

        # Display Results
        if results:
            for result in results:
                st.write(f"**{result['title']}**")
                st.write(f"[{result['link']}]({result['link']})")
                st.write(result["snippet"])
                if result["image"] and is_valid_url(result["image"]):
                    st.image(result["image"], width=400)
                else:
                    st.write("_No image available._")
                st.write("---")
        else:
            st.write("No results found.")

# Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. 
    Developed by ECLOGIC.
    """)

def search_google_cse(query, site=None):
    """
    Perform a Google Custom Search API query.
    Args:
        query (str): Search term.
        site (str): Specific site to search (e.g., tiktok.com).
    Returns:
        list: A list of search results (title, link, snippet, image).
    """
    url = "https://www.googleapis.com/customsearch/v1"
    params = {
        "q": f"{query} site:{site}" if site else query,
        "key": API_KEY,
        "cx": CSE_ID,
    }
    response = requests.get(url, params=params)
    data = response.json()
    results = []
    if "items" in data:
        for item in data["items"]:
            results.append({
                "title": item["title"],
                "link": item["link"],
                "snippet": item.get("snippet", ""),
                "image": item.get("pagemap", {}).get("cse_image", [{}])[0].get("src"),
            })
    return results

def is_valid_url(url):
    """
    Check if a URL is valid.
    Args:
        url (str): The URL to validate.
    Returns:
        bool: True if valid, False otherwise.
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.netloc) and bool(parsed.scheme)
    except Exception:
        return False

if __name__ == "__main__":
    main()
