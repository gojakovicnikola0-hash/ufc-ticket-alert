import os
import requests

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

headers = {
    "User-Agent": "Mozilla/5.0"
}

response = requests.get(URL, headers=headers)

if response.status_code == 200:
    text = f"✅ UFC stranica je dostupna.\n\n{URL}"
else:
    text = f"❌ Greška {response.status_code} prilikom otvaranja stranice."

requests.post(
    f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
    data={
        "chat_id": CHAT_ID,
        "text": text
    }
)
