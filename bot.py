

import os
import json
import asyncio
from playwright.async_api import async_playwright
from telegram import Bot


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EVENT_URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

bot = Bot(token=BOT_TOKEN)

found_tickets = False


async def send_telegram(message):
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )
        print("Telegram poslat")
    except Exception as e:
        print("Telegram greska:", e)


def check_available(data):

    global found_tickets

    try:
        text = json.dumps(data)

        if "Available" in text:

            if not found_tickets:
                found_tickets = True
                return True

    except:
        pass

    return False



async def check_tickets():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        async def handle_response(response):

            url = response.url

            if "seatmap" in url:

                print("SEATMAP:", url)

                try:
                    data = await response.json()

                    if check_available(data):

                        await send_telegram(
                            "🔥 UFC KARTE SU DOSTUPNE!\n\n"
                            "https://tickets.rs/event/ufc_fight_night_belgrade_26702"
                        )

                except Exception as e:
                    print("JSON greska:", e)



        page.on(
            "response",
            handle_response
        )


        await page.goto(
            EVENT_URL,
            wait_until="networkidle"
        )


        print("Stranica otvorena")


        await page.wait_for_timeout(15000)


        await browser.close()



async def main():

    await check_tickets()



if __name__ == "__main__":

    asyncio.run(main())
