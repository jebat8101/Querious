import streamlit as st
import os
import json
import asyncio
import datetime
from dotenv import load_dotenv
from telethon.sync import TelegramClient
from telethon.errors.rpcerrorlist import PhoneNumberBannedError, UsernameInvalidError

# Load environment variables
load_dotenv()

# Streamlit app title
st.title("Telegram Phone Checker")

# Load API credentials from environment variables
api_id = os.getenv("APP_API_ID", "1807430")
api_hash = os.getenv("APP_API_HASH", "ee09343af2a246aeb9c130c9e74a0179")

# Helper function to serialize JSON safely
def json_serializer(obj):
    if isinstance(obj, bytes):
        return obj.decode("utf-8", "ignore")  # Decode bytes to string
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()  # Convert datetime to ISO format string
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")

# Function to check a phone number
async def check_phone(phone):
    async with TelegramClient("session_name", api_id, api_hash) as client:
        try:
            user = await client.get_entity(phone)
            return user.to_dict()
        except PhoneNumberBannedError:
            return {"error": "Phone number is banned"}
        except Exception as e:
            return {"error": str(e)}

# Function to check a username
async def check_username(username):
    async with TelegramClient("session_name", api_id, api_hash) as client:
        try:
            user = await client.get_entity(username)
            return user.to_dict()
        except UsernameInvalidError:
            return {"error": "Invalid username"}
        except Exception as e:
            return {"error": str(e)}

# Options selection
option = st.selectbox("Select an option", [
    "Check phone number",
    "Check phone numbers from file",
    "Check username",
    "Check usernames from file",
    "Clear saved credentials"
])

if option == "Check phone number":
    phone = st.text_input("Enter phone number (with country code)")
    if st.button("Check Telegram Account"):
        result = asyncio.run(check_phone(phone))
        st.json(result)
        with open(f"results/{phone}.json", "w") as f:
            json.dump(result, f, indent=4, default=json_serializer)
        st.success("Result saved successfully!")

elif option == "Check phone numbers from file":
    uploaded_file = st.file_uploader("Upload a file containing phone numbers", type=["txt"])
    if uploaded_file and st.button("Check Numbers"):
        phone_numbers = uploaded_file.read().decode("utf-8").splitlines()
        results = {}
        for phone in phone_numbers:
            results[phone] = asyncio.run(check_phone(phone))
        st.json(results)
        with open("results/phones_results.json", "w") as f:
            json.dump(results, f, indent=4, default=json_serializer)
        st.success("Results saved successfully!")

elif option == "Check username":
    username = st.text_input("Enter Telegram username")
    if st.button("Check Telegram Account"):
        result = asyncio.run(check_username(username))
        st.json(result)
        with open(f"results/{username}.json", "w") as f:
            json.dump(result, f, indent=4, default=json_serializer)
        st.success("Result saved successfully!")

elif option == "Check usernames from file":
    uploaded_file = st.file_uploader("Upload a file containing usernames", type=["txt"])
    if uploaded_file and st.button("Check Usernames"):
        usernames = uploaded_file.read().decode("utf-8").splitlines()
        results = {}
        for username in usernames:
            results[username] = asyncio.run(check_username(username))
        st.json(results)
        with open("results/usernames_results.json", "w") as f:
            json.dump(results, f, indent=4, default=json_serializer)
        st.success("Results saved successfully!")

elif option == "Clear saved credentials":
    if st.button("Clear Session Data"):
        os.remove("session_name.session") if os.path.exists("session_name.session") else None
        st.success("Session data cleared!")
st.caption("Powered by Eclogic ")
