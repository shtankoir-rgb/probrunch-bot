import asyncio
import os
import threading
import json

from flask import Flask
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, FSInputFile

# ================== ENV ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")

MODERATOR_IDS = [
    int(x) for x in os.getenv("MODERATOR_IDS", "").split(",") if x
]

MAP_LINK = "https://maps.app.goo.gl/d5cZUQbqf8exr11X7"
USERS_FILE = "users.json"

# ================== INIT ==================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting_for_question = set()
waiting_for_broadcast = set()

# ================== USERS STORAGE ==================

def load_users():
    if not os.path.exists(USERS_FILE):
        return []
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_user(user_id):
    users = load_users()
    if user_id not in users:
        users.append(user_id)
        with open(USERS_FILE, "w") as f:
            json.dump(users, f)

# ================== KEYBOARD ==================

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="❓ Питання / відповіді")],
        [KeyboardButton(text="📄 Програма")],
        [KeyboardButton(text="📍 Точка на мапі")],
        [KeyboardButton(text="🍷 Корисна інформація")]
    ],
    resize_keyboard=True
)

# ================== START ==================

@dp.message(Command("start"))
async def start(message: types.Message):
    save_user(message.from_user.id)

    start_text = (
        "Вітаємо у чат-боті PRO BRUNCH від METRO 🍷\n\n"
        "Раді бачити вас серед гостей нашого бранчу!\n\n"
        "Тут ви знайдете:\n"
        "• програму вечора\n"
        "• точку локації на мапі\n"
        "• корисну інформацію\n\n"
        "А якщо у вас виникнуть будь-які запитання —\n"
        "просто натисніть «❓ Питання / відповіді»,\n"
        "і ми з радістю допоможемо.\n\n"
        "До зустрічі на PRO BRUNCH ✨"
    )

    await message.answer(start_text, reply_markup=main_keyboard)
    await message.answer_photo(FSInputFile("files/invitation.jpg"))

# ================== BROADCAST ==================

@dp.message(Command("broadcast"))
async def broadcast_command(message: types.Message):
    if message.from_user.id not in MODERATOR_IDS:
        return

    waiting_for_broadcast.add(message.from_user.id)
    await message.answer(
        "✍️ Напишіть текст розсилки.\n"
        "Він буде надісланий ВСІМ користувачам."
    )

# ================== MAIN HANDLER ==================

@dp.message()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text or ""

    save_user(user_id)

    # --- BROADCAST TEXT ---
    if user_id in waiting_for_broadcast:
        waiting_for_broadcast.remove(user_id)
        users = load_users()

        sent = 0
        for uid in users:
            try:
                await bot.send_message(uid, text)
                sent += 1
            except:
                pass

        await message.answer(f"✅ Розсилка надіслана {sent} користувачам.")
        return

    # --- ПИТАННЯ / ВІДПОВІДІ ---
    if "Питання" in text:
        if user_id in waiting_for_question:
            return
        waiting_for_question.add(user_id)
        await message.answer(
            "✍️ Напишіть ваше питання.\n"
            "Модератор відповість вам особисто."
        )
        return

    # --- ТЕКСТ ПИТАННЯ ---
    if user_id in waiting_for_question:
        waiting_for_question.remove(user_id)

        for mod_id in MODERATOR_IDS:
            await bot.send_message(
                mod_id,
                f"❓ ПИТАННЯ ВІД ГОСТЯ\n\n"
                f"{message.from_user.full_name}\n"
                f"(id: {user_id})\n\n"
                f"{text}\n\n"
                f"⬇️ Щоб відповісти гостю, натисніть REPLY на це повідомлення"
            )

        await message.answer("✅ Дякуємо! Питання передано модераторам.")
        return

    # --- ПРОГРАМА ---
    if "Програма" in text:
        await message.answer_photo(FSInputFile("files/program.jpg"))
        return

    # --- МАПА ---
    if "Точка" in text:
        await message.answer(f"📍 Локація заходу:\n{MAP_LINK}")
        return

    # --- КОРИСНА ІНФОРМАЦІЯ (ЗАГЛУШКА) ---
    if "Корисна" in text:
        await message.answer(
            "🍷 Невдовзі тут з'явиться корисна інформація.\n"
            "Залишайтеся з нами ✨"
        )
        return

    # --- REPLY ВІД МОДЕРАТОРА ---
    if user_id in MODERATOR_IDS and message.reply_to_message:
        if "(id:" in message.reply_to_message.text:
            try:
                uid = int(
                    message.reply_to_message.text
                    .split("(id:")[1]
                    .split(")")[0]
                )
                await bot.send_message(
                    uid,
                    f"💬 Відповідь модератора:\n\n{message.text}"
                )
            except:
                pass

# ================== FLASK (RENDER FREE) ==================

app = Flask(__name__)

@app.route("/")
def home():
    return "OK"

def run_flask():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

async def run_bot():
    await dp.start_polling(bot)

# ================== START ==================

if __name__ == "__main__":
    threading.Thread(target=run_flask).start()
    asyncio.run(run_bot())
