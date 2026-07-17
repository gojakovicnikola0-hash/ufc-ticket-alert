import os
import json
import asyncio
import re
from playwright.async_api import async_playwright
from telegram import Bot


BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

EVENT_URL = "https://tickets.rs/event/ufc_fight_night_belgrade_26702"

bot = Bot(token=BOT_TOKEN)


async def send_telegram(message):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )
    print("Telegram poslat")


def find_numbers(data):

    found = []

    text = json.dumps(data)

    # svi brojevi iza Available
    values = re.findall(
        r'"Available"\s*:\s*(\d+)',
        text
    )

    for v in values:
        found.append(int(v))

    return sum(found)



async def check_tickets():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        sent = False


        async def handle_response(response):

            nonlocal sent

            if "seatmap" in response.url:

                print("SEATMAP:", response.url)

                try:
                    data = await response.json()

                    available = find_numbers(data)

                    print("UKUPNO:", available)

                    # ispis prvog dela odgovora za analizu
                    print(json.dumps(data)[:3000])


                    if available > 0 and not sent:

                        sent = True

                        await send_telegram(
                            "🔥 UFC KARTE DOSTUPNE!\n\n"
                            f"Broj: {available}\n\n"
                            f"{EVENT_URL}"
                        )


                except Exception as e:
                    print("GRESKA:", e)



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
