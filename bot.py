import asyncio
import os
import threading

from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)

# ================== ENV ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODERATOR_ID = int(os.getenv("MODERATOR_ID"))

MAP_LINK = "https://maps.app.goo.gl/d5cZUQbqf8exr11X7"

# ================== BOT ==================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting_for_question = set()

# ================== KEYBOARDS ==================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Питання / відповіді")],
        [KeyboardButton(text="📄 Програма")],
        [KeyboardButton(text="📍 Точка на мапі")],
        [KeyboardButton(text="🍷 Корисна інформація")]
    ],
    resize_keyboard=True
)

useful_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="🍷 Інформація про вина", callback_data="wine")],
        [InlineKeyboardButton(text="📦 Інформація про товари", callback_data="products")]
    ]
)

# ================== START ==================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Вітаємо у чат-боті PRO BRUNCH від METRO 🍷\n\n"
        "Раді бачити вас серед гостей нашого бранчу!\n\n"
        "Тут ви знайдете:\n"
        "• програму вечора\n"
        "• точку локації на мапі\n"
        "• корисну інформацію\n\n"
