import streamlit as st
import requests
import random
import time
from hashlib import md5
from bs4 import BeautifulSoup
from urllib.parse import urlencode

class Hawker:
    def __init__(self):
        self.headers = {
            "User-Agent": random.choice([
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/97.0.4692.71 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/98.0.4758.80 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:97.0) "
                "Gecko/20100101 Firefox/97.0"
            ]),
            "Accept-Language": "en-US,en;q=0.9",
            "Referer": "https://www.google.com",
            "Origin": "https://www.google.com"
        }

    # ------------------ EMAIL CHECKS ------------------
    def check_github_email(self, email):
        """
        Check if a GitHub account is associated with the email.
        Returns a list of user objects if found, else empty list.
        """
        url = f"https://api.github.com/search/users?q={email}+in:email"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                result = response.json()
                if result.get("total_count", 0) > 0:
                    return result["items"]  # list of user objects
                else:
                    return []
            else:
                return []
        except Exception:
            return []

    def check_spotify_email(self, email):
        """
        Check if a Spotify account might be associated with the email.
        status == 20 => email in use
        """
        url = f"https://spclient.wg.spotify.com/signup/public/v1/account?validate=1&email={email}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                return (data.get('status') == 20)
            return False
        except Exception:
            return False

    def check_twitter_email(self, email):
        """
        Basic check for Twitter (X).
        If data["valid"] == False => the email is taken => account found.
        If data["valid"] == True  => the email is available => no account found.
        """
        url = f"https://api.twitter.com/i/users/email_available.json?email={email}"
        try:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                # valid == False => Account Found
                return (data.get("valid") == False)
            return False
        except Exception:
            return False

    def check_gravatar_email(self, email):
        """
        Check if an email has a Gravatar profile.
        If status 200 => Found
        """
        email_hash = md5(email.strip().lower().encode()).hexdigest()
        url = f"https://en.gravatar.com/{email_hash}.json"
        try:
            response = requests.get(url, headers=self.headers)
            return (response.status_code == 200)
        except Exception:
            return False

    def check_pinterest_email(self, email):
        """
        Check if a Pinterest account is associated with the email.
        If data["resource_response"]["data"] is truthy => found
        """
        params = {
            "source_url": "/",
            "data": '{"options": {"email": "' + email + '"}, "context": {}}'
        }
        try:
            response = requests.get(
                "https://www.pinterest.fr/resource/EmailExistsResource/get/",
                params=params,
                headers=self.headers
            )
            if response.status_code == 200:
                data = response.json()
                # If data["resource_response"]["data"] is truthy => found
                return bool(data["resource_response"]["data"])
            return False
        except Exception:
            return False

    def check_duolingo_email(self, email):
        """
        Check Duolingo by searching user with the email.
        If data["users"] is non-empty => account found.
        """
        url = "https://www.duolingo.com/2017-06-30/users"
        params = {"email": email}
        try:
            response = requests.get(url, params=params, headers=self.headers)
            if response.status_code == 200:
                data = response.json()
                if data.get("users"):
                    return True
            return False
        except Exception:
            return False

    # ------------------ USERNAME SEARCH ------------------
    def username_search(self, username):
        """
        Attempts to access known social/content sites with the given username.
        Returns a list of (url, status_code).
        """
        urls = [
            f'https://www.youtube.com/@{username}',
            f'https://github.com/{username}',
            f'https://open.spotify.com/user/{username}',
            f'https://pastebin.com/u/{username}',
            f'https://soundcloud.com/{username}'
            # Add or remove platforms as needed
        ]
        results = []
        for url in urls:
            try:
                resp = requests.get(url, headers=self.headers, allow_redirects=False, timeout=5)
                results.append((url, resp.status_code))
            except requests.RequestException:
                results.append((url, 0))
            time.sleep(0.05)
        return results

    # ------------------ IP GEOLOCATION ------------------
    def geolocation_ip(self, ip_address):
        """
        Fetch IP geolocation from ipwhois.app
        """
        url = f"https://ipwhois.app/json/{ip_address}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {}
        except Exception:
            return {}

    # ------------------ PHONE NUMBER LOOKUP ------------------
    def get_phone_info(self, phone_number):
        """
        Example phone info lookup - placeholder API for demonstration.
        You may replace it with your own phone lookup service.
        """
        url = f"http://phone-number-api.com/json/?number={phone_number}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            return None
        except Exception:
            return None

    # ------------------ MAC ADDRESS LOOKUP ------------------
    def mac_address_lookup(self, mac):
        """
        Example MAC lookup from api.maclookup.app
        """
        url = f"https://api.maclookup.app/v2/macs/{mac}"
        try:
            resp = requests.get(url, headers=self.headers)
            data = resp.json()
            if data.get("success") and data.get("found"):
                return data
            else:
                return {"error": "Not found or invalid MAC address."}
        except Exception as e:
            return {"error": str(e)}

    # ------------------ BITCOIN LOOKUP ------------------
    def get_bitcoin_info(self, bitcoin):
        """
        Returns raw data from Blockchain.info about the address.
        """
        url = f"https://blockchain.info/rawaddr/{bitcoin}"
        try:
            resp = requests.get(url, headers=self.headers)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {"error": f"Status code: {resp.status_code}"}
        except Exception as e:
            return {"error": str(e)}

    # ------------------ DOXBIN SEARCH ------------------
    def doxbin_search(self, query_text):
        """
        Google dork: <text> site:doxbin.org
        """
        query = f"{query_text} site:doxbin.org"
        params = {'q': query, 'hl': 'en', 'num': 10}
        url_with_params = "https://www.google.com/search?" + urlencode(params)
        try:
            resp = requests.get(url_with_params, headers=self.headers)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, 'html.parser')
            links = []
            for a in soup.find_all('a', href=True):
                href = a['href']
                if href.startswith('/url?q='):
                    link = href.split('/url?q=')[1].split('&')[0]
                    # Filter out google.com, etc.
                    if ('doxbin.org' in link
                            and not any(sub in link for sub in
                                        ['google.com', 'translate.google.com', 'accounts.google.com'])):
                        links.append(link)
            return links
        except requests.RequestException:
            return []


# ----------------- STREAMLIT APPLICATION -----------------

def main():
    st.title("🕵️ Hawker OSINT Investigator")

    st.write(
        "Hawker OSINT Investigator is a Streamlit-based tool designed for open-source intelligence (OSINT) gathering. "
        "It helps cybersecurity professionals, law enforcement, and researchers collect and analyze publicly available "
        "data from various sources. Enter the required information, and the tool will retrieve relevant OSINT data."
    )

    st.sidebar.header("Select an Operation")
    operation = st.sidebar.selectbox(
        "Operations",
        (
            "Email Checks",
            "Username Search",
            "IP Geolocation",
            "Phone Number Lookup",
            "MAC Address Lookup",
            "Bitcoin Address Info",
            "Doxbin Search"
        )
    )

    haw = Hawker()

    # ----------------- EMAIL CHECKS (MULTIPLE SITES) -----------------
    if operation == "Email Checks":
        st.subheader("Check multiple services for an Email")

        email_input = st.text_input("Enter Email Address")
        if st.button("Check Email"):
            if email_input.strip() == "":
                st.warning("Please enter a valid email address.")
            else:
                with st.spinner("Checking multiple services..."):
                    # 1) GitHub
                    github_info = haw.check_github_email(email_input)
                    github_found = len(github_info) > 0

                    # 2) Spotify
                    spotify_found = haw.check_spotify_email(email_input)

                    # 3) Twitter
                    twitter_found = haw.check_twitter_email(email_input)

                    # 4) Gravatar
                    gravatar_found = haw.check_gravatar_email(email_input)

                    # 5) Pinterest
                    pinterest_found = haw.check_pinterest_email(email_input)

                    # 6) Duolingo
                    duolingo_found = haw.check_duolingo_email(email_input)

                # Build a results table
                table_data = [
                    {"Service": "GitHub",    "Found": "Yes" if github_found else "No"},
                    {"Service": "Spotify",   "Found": "Yes" if spotify_found else "No"},
                    {"Service": "Twitter/X", "Found": "Yes" if twitter_found else "No"},
                    {"Service": "Gravatar",  "Found": "Yes" if gravatar_found else "No"},
                    {"Service": "Pinterest", "Found": "Yes" if pinterest_found else "No"},
                    {"Service": "Duolingo",  "Found": "Yes" if duolingo_found else "No"},
                ]
                st.table(table_data)

                # Show GitHub details if found
                if github_found:
                    st.markdown("**GitHub Details**:")
                    details_table = []
                    for item in github_info:
                        details_table.append({
                            "Username": item.get("login", ""),
                            "Profile": f"https://github.com/{item.get('login','')}",
                            "User ID": item.get("id", "")
                        })
                    st.table(details_table)

    # ----------------- USERNAME SEARCH -----------------
    elif operation == "Username Search":
        st.subheader("Check if a username exists on various platforms (Found / Not Found)")

        username_input = st.text_input("Enter Username")
        if st.button("Search Username"):
            if not username_input.strip():
                st.warning("Please enter a valid username.")
            else:
                results = haw.username_search(username_input)
                if results:
                    table_data = []
                    for url, status in results:
                        # 200 => Found, else => Not Found
                        result_text = "Found" if status == 200 else "Not Found"
                        table_data.append({"URL": url, "Result": result_text})
                    st.table(table_data)
                else:
                    st.warning("No results or an error occurred.")

    # ----------------- IP GEOLOCATION -----------------
    elif operation == "IP Geolocation":
        st.subheader("Geolocate an IP address")
        ip_input = st.text_input("Enter IP (IPv4 or IPv6)")
        if st.button("Geolocate IP"):
            info = haw.geolocation_ip(ip_input)
            if info:
                table_data = [{"Field": k, "Value": v} for k, v in info.items()]
                st.table(table_data)
            else:
                st.error("Failed to retrieve IP geolocation data.")

    # ----------------- PHONE NUMBER LOOKUP -----------------
    elif operation == "Phone Number Lookup":
        st.subheader("Look up basic phone number info")
        phone_input = st.text_input("Enter Phone Number (e.g. +1 XXX...)")
        if st.button("Lookup Phone"):
            data = haw.get_phone_info(phone_input)
            if data:
                table_data = [{"Field": k, "Value": v} for k, v in data.items()]
                st.table(table_data)
            else:
                st.error("No data found or error in lookup.")

    # ----------------- MAC ADDRESS LOOKUP -----------------
    elif operation == "MAC Address Lookup":
        st.subheader("Lookup Manufacturer Info by MAC Address")
        mac_input = st.text_input("Enter MAC address (e.g. 44:38:39:ff:ef:57)")
        if st.button("Lookup MAC"):
            data = haw.mac_address_lookup(mac_input)
            if isinstance(data, dict):
                table_data = [{"Field": k, "Value": v} for k, v in data.items()]
                st.table(table_data)
            else:
                st.error("Error retrieving data or unexpected response.")

    # ----------------- BITCOIN ADDRESS INFO -----------------
    elif operation == "Bitcoin Address Info":
        st.subheader("Get Bitcoin address info")
        btc_input = st.text_input("Enter BTC Address")
        if st.button("Lookup BTC"):
            info = haw.get_bitcoin_info(btc_input)
            if info and "error" not in info:
                # Show relevant fields in a table
                fields_of_interest = {
                    "Final Balance (BTC)": info.get("final_balance", 0) / 1e8,
                    "Total Transactions": info.get("n_tx", 0),
                    "Total Received (BTC)": info.get("total_received", 0) / 1e8
                }
                table_data = [{"Field": k, "Value": v} for k, v in fields_of_interest.items()]
                st.table(table_data)

                st.write("**Raw JSON**:")
                st.json(info)
            else:
                st.error(f"Error retrieving data: {info.get('error')}")

    # ----------------- DOXBIN SEARCH -----------------
    elif operation == "Doxbin Search":
        st.subheader("Search Doxbin.org references via Google Dorking")
        query_text = st.text_input("Enter search text")
        if st.button("Search Doxbin"):
            links = haw.doxbin_search(query_text)
            if links:
                st.success("Results found:")
                table_data = [{"Link": link} for link in links]
                st.table(table_data)
            else:
                st.warning("No relevant results found.")

# Footer with Copyright
    st.markdown("""
    ---
    © 2025, All rights reserved. Developed by ECLOGIC.
    """)

if __name__ == "__main__":
    main()
