import streamlit as st 
import requests 
import re 
from googlesearch import search 
from phonenumbers import parse, is_valid_number, format_number, PhoneNumberFormat 

class UsernameOSINT: 
    def __init__(self, username): 
        self.username = username 
        self.results = {} 
        self.headers = { 
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' 
        } 
        self.email_pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}') 
        self.phone_pattern = re.compile(r'\+?[1-9][0-9]{7,14}') 

    def check_github(self): 
        try: 
            response = requests.get(f"https://api.github.com/users/{self.username}", headers=self.headers) 
            if response.status_code == 200: 
                data = response.json() 
                return { 
                    "exists": True, "name": data.get("name"), "bio": data.get("bio"), 
                    "location": data.get("location"), "public_repos": data.get("public_repos"), 
                    "followers": data.get("followers"), "following": data.get("following"), 
                    "profile_url": data.get("html_url"), "email": data.get("email") 
                } 
        except Exception as e: 
            return {"exists": False, "error": str(e)} 
        return {"exists": False} 

    def check_instagram(self): 
        try: 
            response = requests.get(f"https://www.instagram.com/{self.username}/", headers=self.headers) 
            return {"exists": response.status_code == 200} 
        except Exception as e: 
            return {"exists": False, "error": str(e)} 

    def check_twitter(self): 
        try: 
            response = requests.get(f"https://twitter.com/{self.username}", headers=self.headers) 
            return {"exists": response.status_code == 200} 
        except Exception as e: 
            return {"exists": False, "error": str(e)} 

    def search_whatsapp(self): 
        found_numbers = set() 
        search_query = f"{self.username} whatsapp contact" 
        try: 
            search_results = search(search_query, num_results=10) 
            for url in search_results: 
                try: 
                    response = requests.get(url, headers=self.headers, timeout=5) 
                    if response.status_code == 200: 
                        numbers = self.phone_pattern.findall(response.text) 
                        for number in numbers: 
                            try: 
                                parsed_number = parse(number) 
                                if is_valid_number(parsed_number): 
                                    formatted_number = format_number(parsed_number, PhoneNumberFormat.INTERNATIONAL) 
                                    found_numbers.add(formatted_number) 
                            except: 
                                continue 
                except: 
                    continue 
        except Exception as e: 
            return [] 
        return list(found_numbers) 

    def search_emails(self): 
        found_emails = set() 
        search_query = f"{self.username} email contact" 
        try: 
            search_results = search(search_query, num_results=10) 
            for url in search_results: 
                try: 
                    response = requests.get(url, headers=self.headers, timeout=5) 
                    if response.status_code == 200: 
                        emails = self.email_pattern.findall(response.text) 
                        found_emails.update(emails) 
                except: 
                    continue 
        except Exception as e: 
            return [] 
        return list(found_emails) 

def username_osint_main(): 
    """ Streamlit interface for OSINT Username Finder. """
    st.title("🔍 OSINT Username Finder")  # Removed st.set_page_config()
    st.write(
        "This tool helps investigators, cybersecurity professionals, and researchers gather "
        "open-source intelligence (OSINT) on a specific username. It scans multiple platforms "
        "to identify potential accounts, associated information, and digital footprints linked "
        "to the provided username."
    )


    st.sidebar.header("Search Options") 
    username = st.sidebar.text_input("Enter a username to search", help="Input the username to find associated profiles and contact details.") 
    search_social = st.sidebar.checkbox("Search Social Media", value=True) 
    search_contacts = st.sidebar.checkbox("Search Emails and WhatsApp", value=True) 

    if st.sidebar.button("Start Search"): 
        if username: 
            osint = UsernameOSINT(username) 
            if search_social: 
                st.subheader("Social Media Profiles") 
                github = osint.check_github() 
                if github["exists"]: 
                    st.success(f"GitHub profile found: [Link]({github['profile_url']})") 
                    with st.expander("GitHub Details"): 
                        st.json(github) 
                else: 
                    st.error("No GitHub profile found.") 

                instagram = osint.check_instagram() 
                if instagram["exists"]: 
                    st.success("Instagram profile found.") 
                else: 
                    st.error("No Instagram profile found.") 

                twitter = osint.check_twitter() 
                if twitter["exists"]: 
                    st.success("Twitter profile found.") 
                else: 
                    st.error("No Twitter profile found.") 

            if search_contacts: 
                st.subheader("WhatsApp Numbers") 
                whatsapp_numbers = osint.search_whatsapp() 
                if whatsapp_numbers: 
                    st.success("Potential WhatsApp numbers found:") 
                    st.write(whatsapp_numbers) 
                else: 
                    st.error("No WhatsApp numbers found.") 

                st.subheader("Email Addresses") 
                emails = osint.search_emails() 
                if emails: 
                    st.success("Potential email addresses found:") 
                    st.write(emails) 
                else: 
                    st.error("No email addresses found.") 
        else: 
            st.warning("Please enter a username to search.") 

# Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. Developed by ECLOGIC.
    """)


