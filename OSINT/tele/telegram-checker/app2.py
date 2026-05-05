from fastapi import FastAPI, HTTPException, Query, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from telethon import TelegramClient, errors
from telethon.tl.functions.contacts import ImportContactsRequest, DeleteContactsRequest
from telethon.tl import types
import os
import asyncio
from dotenv import load_dotenv
import nest_asyncio

# Load environment variables
load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
SESSION_NAME = "telegram_checker_session"

app = FastAPI(title="Telegram Account Checker")

client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

async def get_client():
    if not client.is_connected():
        await client.connect()
    return client

@app.get("/", response_class=HTMLResponse)
async def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Telegram Checker</title>
        <script>
            async function checkTelegram() {
                const input = document.getElementById("input").value;
                const type = document.querySelector('input[name="type"]:checked').value;
                const response = await fetch(`/${type}?q=${input}`);
                const data = await response.json();
                document.getElementById("result").innerText = JSON.stringify(data, null, 2);
            }
        </script>
    </head>
    <body>
        <h2>Telegram Account Checker</h2>
        <input id="input" placeholder="Enter phone number or username"> <br>
        <input type="radio" name="type" value="check_phone" checked> Phone
        <input type="radio" name="type" value="check_username"> Username
        <button onclick="checkTelegram()">Check</button>
        <pre id="result"></pre>
    </body>
    </html>
    """

@app.get("/check_phone")
async def check_phone(q: str = Query(...), client: TelegramClient = Depends(get_client)):
    try:
        contact = types.InputPhoneContact(client_id=0, phone=q, first_name="Test", last_name="User")
        result = await client(ImportContactsRequest([contact]))
        if not result.users:
            return JSONResponse(content={"error": "No Telegram account found"})
        user = result.users[0]
        await client(DeleteContactsRequest(id=[user.id]))
        return {"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name}
    except errors.PhoneNumberInvalidError:
        raise HTTPException(status_code=400, detail="Invalid phone number format")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/check_username")
async def check_username(q: str = Query(...), client: TelegramClient = Depends(get_client)):
    try:
        user = await client.get_entity(q)
        if not isinstance(user, types.User):
            return JSONResponse(content={"error": "No Telegram account found"})
        return {"id": user.id, "username": user.username, "first_name": user.first_name, "last_name": user.last_name}
    except errors.UsernameNotOccupiedError:
        raise HTTPException(status_code=404, detail="Username not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn

    nest_asyncio.apply()
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(client.connect())

    uvicorn.run(app, host="0.0.0.0", port=8000)
