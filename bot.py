import asyncio
import logging
import os
import sys
import threading
from datetime import datetime



from aiohttp import web
from aiogram import Bot, Dispatcher, Router, html, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, PreCheckoutQuery, ReplyKeyboardRemove, SuccessfulPayment

from db import add_user, fetch_all_stories, add_story
from kbs import get_keyboard
from funcs import contains_bad_words
import random

# Bot token
TOKEN = "7846714351:AAE83l5lAp-rfSWx0tNL1q5_kXJiD694wnk"

# Initialize FastAPI and Aiogram components

dp = Dispatcher()
router = Router()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

# A dictionary to track sent stories per user
user_sent_stories = {}

# Prices for premium subscription
prices = [
    types.LabeledPrice(label="Bir oylik Premium", amount=5000000),  # Amount in minor units (50000 = 500.00 UZS)
]
@router.message(Command("premium"))
async def admin_panel(message: Message):
    await bot.send_invoice(
        chat_id=message.chat.id,
        title="Bir oylik Premium Obuna",
        description="Premium funksiyalardan foydalanish uchun 1 oylik obuna.",
        payload="subscription_monthly",
        provider_token="398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065",
        currency="UZS",
        prices=prices,
        start_parameter="buy_monthly_subscription"
    )

@router.pre_checkout_query()
async def process_pre_checkout_query(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@router.message(types.SuccessfulPayment)
async def successful_payment(message: SuccessfulPayment):
    logging.info(f"Successful payment data: {message.successful_payment}")
    try:
        if message.successful_payment.invoice_payload == "subscription_monthly":
            # Add subscription logic here (function to be implemented)
            await message.answer(
                "Obuna bo'lganingiz uchun tashakkur! Sizning premium funksiyalaringiz endi faol. Funksiyalar suhbatdoshni qidirishingizda faollashadi."
            )
            await message.answer("🎉")
    except Exception as e:
        logging.error(f"Error processing successful payment: {e}")
        await message.answer("To'lovni qayta ishlashda xatolik yuz berdi. Iltimos, yana bir bor urinib ko'ring.")

# Routes


# Premium subscription handlers


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

# Story-related handlers
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

@router.message(lambda msg: msg.text == "Upload a story")
async def start_upload_story(message: Message):
    await message.answer("Please upload your story here:", reply_markup=ReplyKeyboardRemove())

@router.message(lambda msg: msg.text and contains_bad_words(msg.text))
async def bad_word_detected(message: Message):
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
    port = int(os.getenv('PORT', 10000))  # Use the PORT environment variable
    logging.info(f"Starting web server on port {port}")
    web.run_app(app, port=port)

# Main function to run the bot
async def main():
    logging.info("Starting bot...")
    dp.include_router(router)

    # Run web server as a task
    asyncio.create_task(start_web_server())

    # Start polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)

    # Run the bot
    asyncio.run(main())
