import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

response = requests.get(URL, headers={
    "User-Agent": "Mozilla/5.0"
})

message = f"✅ Bot radi!\n\nStatus: {response.status_code}\n{URL}"

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": message
    }
)
