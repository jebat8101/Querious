import asyncio
import json
import logging
import os
import pickle
import pandas as pd
import streamlit as st
from pathlib import Path
from dataclasses import dataclass, asdict
from telethon.sync import TelegramClient, errors
from telethon.tl import types
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest

# Configuration
CONFIG_FILE = Path("config.pkl")
PROFILE_PHOTOS_DIR = Path("profile_photos")
RESULTS_DIR = Path("results")
PROFILE_PHOTOS_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

@dataclass
class TelegramUser:
    id: int
    username: str
    first_name: str
    last_name: str
    phone: str
    premium: bool
    verified: bool
    fake: bool
    bot: bool
    last_seen: str

    @classmethod
    async def from_user(cls, client: TelegramClient, user: types.User, phone: str = "") -> 'TelegramUser':
        return cls(
            id=user.id,
            username=user.username or "",
            first_name=user.first_name or "",
            last_name=user.last_name or "",
            phone=phone,
            premium=getattr(user, "premium", False),
            verified=getattr(user, "verified", False),
            fake=getattr(user, "fake", False),
            bot=getattr(user, "bot", False),
            last_seen=get_user_status(user.status),
        )

def get_user_status(status: types.TypeUserStatus) -> str:
    if isinstance(status, types.UserStatusOnline):
        return "Currently online"
    elif isinstance(status, types.UserStatusOffline):
        return f"Last seen: {status.was_online.strftime('%Y-%m-%d %H:%M:%S')}"
    elif isinstance(status, types.UserStatusRecently):
        return "Last seen recently"
    elif isinstance(status, types.UserStatusLastWeek):
        return "Last seen last week"
    elif isinstance(status, types.UserStatusLastMonth):
        return "Last seen last month"
    return "Unknown"

class TelegramChecker:
    def __init__(self):
        self.config = self.load_config()
        self.client = None

    def load_config(self):
        if CONFIG_FILE.exists():
            try:
                with open(CONFIG_FILE, "rb") as f:
                    return pickle.load(f)
            except Exception as e:
                logger.error(f"Error loading config: {e}")
                return {}
        return {}

    def save_config(self):
        with open(CONFIG_FILE, "wb") as f:
            pickle.dump(self.config, f)

    async def initialize(self, api_id, api_hash, phone):
        self.config["api_id"] = api_id
        self.config["api_hash"] = api_hash
        self.config["phone"] = phone
        self.save_config()

        self.client = TelegramClient("telegram_checker_session", api_id, api_hash)
        await self.client.connect()

        if not await self.client.is_user_authorized():
            try:
                await self.client.send_code_request(phone)
                code = st.text_input("Enter Telegram verification code", type="password")

                if not code.strip():
                    st.error("Please enter the verification code.")
                    return

                await self.client.sign_in(phone, code)
                st.success("Successfully authenticated!")

            except errors.SessionPasswordNeededError:
                password = st.text_input("Enter 2FA password", type="password")
                if st.button("Submit Password"):
                    await self.client.sign_in(password=password)

        if not await self.client.is_user_authorized():
            st.error("Login failed. Please check your credentials.")
            return

    async def check_phone_number(self, phone: str):
        try:
            contact = types.InputPhoneContact(client_id=0, phone=phone, first_name="Temp", last_name="Contact")
            await self.client(ImportContactsRequest([contact]))

            user = await self.client.get_entity(phone)
            return await TelegramUser.from_user(self.client, user, phone)

        except errors.FloodWaitError as e:
            st.error(f"Rate limited! Try again in {e.seconds} seconds.")
        except errors.PhoneNumberInvalidError:
            st.error("Invalid phone number format.")
        except errors.UserDeactivatedError:
            st.error("This account is deactivated.")
        except errors.RPCError as e:
            logger.error(f"RPC error: {e}")
            st.error("Error retrieving account info.")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return None

    async def check_username(self, username: str):
        try:
            user = await self.client.get_entity(username)
            return await TelegramUser.from_user(self.client, user, "")

        except errors.UsernameNotOccupiedError:
            return None  # Username does not exist
        except Exception as e:
            logger.error(f"Error fetching username {username}: {e}")
            return None

    async def process_phones(self, phones):
        tasks = [self.check_phone_number(phone.strip()) for phone in phones if phone.strip()]
        results = await asyncio.gather(*tasks)
        return {phone: asdict(user) if user else {"error": "No Telegram account found"} for phone, user in zip(phones, results)}

    async def process_usernames(self, usernames):
        tasks = [self.check_username(username.strip()) for username in usernames if username.strip()]
        results = await asyncio.gather(*tasks)
        return {username: asdict(user) if user else {"error": "No Telegram account found"} for username, user in zip(usernames, results)}

# Streamlit UI
st.set_page_config(page_title="Telegram Account Checker", layout="wide")
st.title("📞 Telegram Account Checker")

telegram_checker = TelegramChecker()

st.sidebar.header("🛠️ API Configuration")
api_id = st.sidebar.text_input("API ID", value=str(telegram_checker.config.get("api_id", "")))
api_hash = st.sidebar.text_input("API Hash", value=telegram_checker.config.get("api_hash", ""), type="password")
phone = st.sidebar.text_input("Phone Number (with country code)", value=telegram_checker.config.get("phone", ""))

if st.sidebar.button("Save & Authenticate"):
    asyncio.run(telegram_checker.initialize(api_id, api_hash, phone))
    st.sidebar.success("Configuration saved!")

st.header("🔍 Choose an option")
option = st.radio("Select an action:", [
    "Check phone numbers from input",
    "Check phone numbers from file",
    "Check usernames from input",
    "Check usernames from file",
    "Clear saved credentials"
])

if option == "Check phone numbers from input":
    phones = st.text_area("Enter phone numbers (one per line)").split("\n")
    if st.button("Check Phone Numbers"):
        with st.spinner("Checking phone numbers..."):
            results = asyncio.run(telegram_checker.process_phones(phones))
        df = pd.DataFrame.from_dict(results, orient="index")
        st.dataframe(df)
        st.download_button("📥 Download JSON", json.dumps(results, indent=2), "results.json", "application/json")

elif option == "Check phone numbers from file":
    uploaded_file = st.file_uploader("Upload a file containing phone numbers")
    if uploaded_file:
        phones = uploaded_file.read().decode("utf-8").splitlines()
        with st.spinner("Checking phone numbers..."):
            results = asyncio.run(telegram_checker.process_phones(phones))
        df = pd.DataFrame.from_dict(results, orient="index")
        st.dataframe(df)

elif option == "Check usernames from input":
    usernames = st.text_area("Enter usernames (one per line)").split("\n")
    if st.button("Check Usernames"):
        with st.spinner("Checking usernames..."):
            results = asyncio.run(telegram_checker.process_usernames(usernames))
        df = pd.DataFrame.from_dict(results, orient="index")
        st.dataframe(df)

elif option == "Check usernames from file":
    uploaded_file = st.file_uploader("Upload a file containing usernames")
    if uploaded_file:
        usernames = uploaded_file.read().decode("utf-8").splitlines()
        with st.spinner("Checking usernames..."):
            results = asyncio.run(telegram_checker.process_usernames(usernames))
        df = pd.DataFrame.from_dict(results, orient="index")
        st.dataframe(df)

elif option == "Clear saved credentials":
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
    st.sidebar.warning("Credentials cleared. Please restart the app.")
