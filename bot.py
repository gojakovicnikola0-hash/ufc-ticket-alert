import os
import json
import asyncio
from playwright.async_api import async_playwright
from telegram import Bot


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EVENT_URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

bot = Bot(token=BOT_TOKEN)

last_available = 0


async def send_telegram(message):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )
    print("Telegram poslat")


def get_available(data):

    total = 0

    try:
        text = json.dumps(data)

        # pronalazi sve Available vrednosti
        import re

        values = re.findall(r'"Available"\s*:\s*(\d+)', text)

        for v in values:
            total += int(v)

    except Exception as e:
        print("Greska:", e)

    return total


async def check_tickets():

    global last_available

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        async def handle_response(response):

            global last_available

            if "seatmap" in response.url:

                print("SEATMAP:", response.url)

                try:
                    data = await response.json()

                    available = get_available(data)

                    print("Dostupno:", available)

                    # samo kada se pojave nove karte
                    if available > 0 and available != last_available:

                        last_available = available

                        await send_telegram(
                            f"🔥 UFC KARTE DOSTUPNE!\n\n"
                            f"Broj dostupnih: {available}\n\n"
                            f"{EVENT_URL}"
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
