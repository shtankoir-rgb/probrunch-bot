import asyncio
import os
import threading
import traceback

from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

print("✅ bot.py loaded")

BOT_TOKEN = os.getenv("BOT_TOKEN")
MODERATOR_IDS = [int(x) for x in os.getenv("MODERATOR_IDS", "").split(",") if x]
MAP_LINK = "https://maps.app.goo.gl/d5cZUQbqf8exr11X7"

print("✅ ENV loaded", MODERATOR_IDS)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting_for_question = set()

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Питання / відповіді")],
        [KeyboardButton(text="📄 Програма")],
        [KeyboardButton(text="📍 Точка на мапі")],
        [KeyboardButton(text="🍷 Корисна інформація")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Вітаємо у чат-боті PRO BRUNCH від METRO 🍷",
        reply_markup=main_keyboard
    )
    await message.answer_photo(FSInputFile("files/invitation.jpg"))

@dp.message()
async def handle_messages(message: types.Message):
    await message.answer("✅ бот живий")

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    print(f"✅ Flask starting on port {port}")
    app.run(host="0.0.0.0", port=port)

async def run_bot():
    print("✅ starting polling")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        threading.Thread(target=run_flask).start()
        asyncio.run(run_bot())
    except Exception:
        print("❌ FATAL ERROR")
        traceback.print_exc()
