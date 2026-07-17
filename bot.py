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
first_load = True


async def send_telegram(message):

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    print("Telegram poslat")



def make_state(data):

    try:

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

    global last_state, first_load


    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        async def handle_response(response):

            global last_state, first_load


            if "seatmap" in response.url:

                try:

                    data = await response.json()

                    state = make_state(data)


                    if not state:
                        return


                    # prvo samo zapamti stanje
                    if first_load:

                        last_state = state

                        print("Početno stanje sačuvano")

                        return


                    # posle toga prati promene
                    if state != last_state:

                        last_state = state

                        await send_telegram(
                            "🔥 UFC PROMENA KARATA!\n\n"
                            "Promenilo se stanje karata.\n\n"
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


        # čekamo da se svi seatmap pozivi završe
        await page.wait_for_timeout(10000)


        first_load = False


        print("Stranica otvorena")


        await page.wait_for_timeout(2000)


        await browser.close()



async def main():

    await check_tickets()



if __name__ == "__main__":

    asyncio.run(main())
