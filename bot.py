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

current_states = []
baseline_state = None
checking_done = False


async def send_telegram(message):

    await bot.send_message(
        chat_id=CHAT_ID,
        text=message
    )

    print("Telegram poslat")



def make_state(data):

    try:

        # pratimo ceo seatmap odgovor
        text = json.dumps(
            data.get("data", {}),
            sort_keys=True
        )

        return hashlib.md5(
            text.encode()
        ).hexdigest()

    except Exception as e:

        print("State greska:", e)
        return None



async def check_tickets():

    global baseline_state, checking_done


    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()


        async def handle_response(response):

            global baseline_state, checking_done


            if "seatmap" in response.url:

                try:

                    data = await response.json()

                    state = make_state(data)

                    if not state:
                        return


                    if not checking_done:

                        current_states.append(state)

                        print(
                            "Ucitavanje stanja:",
                            len(current_states)
                        )

                        return


                    if baseline_state is None:

                        baseline_state = state

                        print(
                            "Osnovno stanje sacuvano"
                        )

                        return


                    if state != baseline_state:

                        baseline_state = state

                        await send_telegram(
                            "🔥 UFC PROMENA KARATA!\n\n"
                            "Promenjena dostupnost karata.\n\n"
                            f"{EVENT_URL}"
                        )

                        print(
                            "Promena poslata"
                        )


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


        # čekamo da se svi početni API pozivi završe
        await page.wait_for_timeout(15000)


        # uzimamo poslednji dobijeni odgovor kao početno stanje
        if current_states:

            baseline_state = current_states[-1]


        checking_done = True


        print(
            "Praćenje aktivno"
        )


        await page.wait_for_timeout(3000)


        await browser.close()



async def main():

    await check_tickets()



if __name__ == "__main__":

    asyncio.run(main())
