import asyncio
import logging
import os
import sys
import threading

from aiohttp import web
from aiogram.filters.command import Command
from aiogram import Bot, Dispatcher, Router, html
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import Message
from datetime import datetime
from aiogram.types import Message, ReplyKeyboardRemove

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

# Handlers for other commands (Read a story, Upload a story, etc.)
@router.message(lambda msg: msg.text == "Read a story")
async def start_read_story(message: Message):
    user_id = message.chat.id
    stories = fetch_all_stories()
    if user_id not in user_sent_stories:
        user_sent_stories[user_id] = set()
    available_stories = [story for story in stories if story[0] not in user_sent_stories[user_id]]
    if available_stories:
        story = random.choice(available_stories)
        user_sent_stories[user_id].add(story[0])
        await message.answer(f"Here is a story:\n\n{story[2]}")
    else:
        await message.answer("No more new stories to read!")

# Story upload handler
@router.message(lambda msg: msg.text == "Upload a story")
async def start_upload_story(message: Message):
    await message.answer("Please upload your story here:", reply_markup=ReplyKeyboardRemove())

@router.message(lambda msg: msg.text and contains_bad_words(msg.text))
async def bad_word_detected(message: Message):
    if True:
        keyboard = get_keyboard()
        await message.answer("Your message contains inappropriate words and cannot be accepted.", reply_markup=keyboard)

@router.message(lambda msg: msg.text and len(msg.text.split()) < 150)
async def story_too_short(message: Message):
    keyboard = get_keyboard()
    await message.answer("Your story is too short! Stories must be at least 150 words long!", reply_markup=keyboard)

@router.message(lambda msg: msg.text and len(msg.text.split()) > 580)
async def story_too_long(message: Message):
    keyboard = get_keyboard()
    await message.answer("Your story is too long! Stories can be at most 580 words!", reply_markup=keyboard)

@router.message(lambda msg: msg.text and 150 <= len(msg.text.split()) <= 580)
async def story_uploaded_success(message: Message):
    keyboard = get_keyboard()
    chat_id = message.chat.id
    add_story(chat_id=chat_id, story=message.text)
    await message.answer("Your story has been successfully uploaded!", reply_markup=keyboard)

# HTTP Keep-Alive Server
async def handle(request):
    return web.Response(text="Bot is alive!")

def start_web_server():
    app = web.Application()
    app.add_routes([web.get('/', handle)])
    port = int(os.getenv('PORT', 8000))  # Use the PORT environment variable
    logging.info(f"Starting web server on port {port}")
    web.run_app(app, port=port)

# Main function to run the bot
async def main():
    logging.info("Starting bot...")
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp.include_router(router)  # Attach the router to the dispatcher

    # Start the web server in a separate thread
    threading.Thread(target=start_web_server, daemon=True).start()

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Run the bot
    asyncio.run(main())
