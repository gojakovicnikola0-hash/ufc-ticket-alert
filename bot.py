import os
import json
import asyncio
import hashlib
from playwright.async_api import async_playwright
from telegram import Bot


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EVENT_URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

bot = Bot(token=BOT_TOKEN)

last_state = None


async def send_telegram(message):

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    print("Telegram poslat")



def make_state(data):

    try:
        # uzimamo samo deo koji predstavlja mapu/karte
        important = data.get("data", {})

        text = json.dumps(
            important,
            sort_keys=True
        )

        return hashlib.md5(
            text.encode()
        ).hexdigest()

    except Exception as e:
        print("State greska:", e)
        return None



async def check_tickets():

    global last_state

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        async def handle_response(response):

            global last_state


            if "seatmap" in response.url:

                try:

                    data = await response.json()

                    state = make_state(data)


                    if state and last_state is None:

                        last_state = state

                        print("Početno stanje sačuvano")


                    elif state != last_state:

                        last_state = state


                        await send_telegram(
                            "🔥 UFC PROMENA KARATA!\n\n"
                            "Promenjena je dostupnost/mesto karata.\n\n"
                            f"{EVENT_URL}"
                        )


                        print("Promena poslata")


                except Exception as e:

                    print(
                        "JSON greska:",
                        e
                    )


        page.on(
            "response",
            handle_response
        )


        await page.goto(
            EVENT_URL,
            wait_until="networkidle"
        )


        print("Stranica otvorena")


        await page.wait_for_timeout(
            15000
        )


        await browser.close()



async def main():

    await check_tickets()



if __name__ == "__main__":

    asyncio.run(main())
