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
    try:
        await bot.send_message(
            chat_id=CHAT_ID,
            text=message
        )
        print("Telegram poslat")

    except Exception as e:
        print("Telegram greska:", e)



def find_real_tickets(data):

    found = 0

    try:

        text = json.dumps(data)

        # traži samo stvarne seat podatke
        patterns = [
            r'"AvailableSeats"\s*:\s*(\d+)',
            r'"FreeSeats"\s*:\s*(\d+)',
            r'"AvailableTickets"\s*:\s*(\d+)',
            r'"SeatsAvailable"\s*:\s*(\d+)'
        ]


        for p in patterns:

            result = re.findall(p, text)

            for x in result:
                found += int(x)


        # ako postoje direktna sedišta
        if "Seat" in text:
            found += len(
                re.findall(
                    r'"Seat"',
                    text
                )
            )


    except Exception as e:
        print("Parser greska:", e)


    return found



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

                try:

                    data = await response.json()


                    print("SEATMAP")

                    print(
                        "KLJUCEVI:",
                        data.keys()
                    )


                    real = find_real_tickets(data)


                    print(
                        "STVARNE KARTE:",
                        real
                    )


                    if real > 0 and not sent:

                        sent = True


                        await send_telegram(
                            "🔥 UFC KARTE DOSTUPNE!\n\n"
                            f"Broj: {real}\n\n"
                            f"{EVENT_URL}"
                        )


                except Exception as e:

                    print(
                        "GRESKA:",
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


        print(
            "Stranica otvorena"
        )


        await page.wait_for_timeout(
            15000
        )


        await browser.close()



async def main():

    await check_tickets()



if __name__ == "__main__":

    asyncio.run(main())
