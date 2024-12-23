import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from datetime import datetime
from threading import Thread
from http.server import SimpleHTTPRequestHandler, HTTPServer

from db import add_user, fetch_all_stories, add_story
from kbs import get_keyboard
from funcs import contains_bad_words
import random

# Bot token
TOKEN = "7846714351:AAE83l5lAp-rfSWx0tNL1q5_kXJiD694wnk"

# Initialize dispatcher and router
dp = Dispatcher()
router = Router()

# A dictionary to track sent stories per user
user_sent_stories = {}

# Start command handler
@router.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    chat_id = message.chat.id
    username = message.from_user.username or "Unknown"
    joined_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    add_user(username, chat_id, joined_date)
    keyboard = get_keyboard()
    await message.answer(
        f"Hello, {html.bold(message.from_user.full_name)}!\n"
        "Welcome to Thisismystory.\n"
        "It is a place where you can share your stories or read others.\n"
        "Please use the buttons below 👇",
        reply_markup=keyboard,
    )

# Story handlers (same as your original code, truncated here for brevity)
# ...

# HTTP server to bind to a port
def start_http_server():
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"Bot is running!")

    port = int(os.environ.get("PORT", 5000))  # Default to 5000 if PORT is not set
    server = HTTPServer(("0.0.0.0", port), Handler)
    logging.info(f"Starting HTTP server on port {port}")
    server.serve_forever()

# Main function
async def main() -> None:
    logging.info("Starting bot...")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    
    # Start the HTTP server in a separate thread
    http_thread = Thread(target=start_http_server, daemon=True)
    http_thread.start()

    # Run the bot
    asyncio.run(main())
