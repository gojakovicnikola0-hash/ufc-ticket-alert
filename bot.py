
import os
import json
import asyncio
import requests
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


async def check_tickets():

    async with async_playwright() as p:

        browser = await p.chromium.launch(
            headless=True
        )

        page = await browser.new_page()

        await page.goto(
            EVENT_URL,
            wait_until="networkidle"
        )

        print("Stranica otvorena")

        await page.wait_for_timeout(5000)

        content = await page.content()

        with open("page.html", "w", encoding="utf-8") as f:
            f.write(content)

        print("HTML sacuvan")

        await browser.close()


async def main():
    await check_tickets()


if __name__ == "__main__":
    asyncio.run(main())
