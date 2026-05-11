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

# ================== INIT ==================

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

# ================== MAIN HANDLER ==================

@dp.message()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text or ""

    # --- 1. КНОПКА "ПИТАННЯ / ВІДПОВІДІ" ---
    if "Питання" in text:
        # ✅ якщо користувач уже в режимі питання — НІЧОГО не робимо
        if user_id in waiting_for_question:
            return

        waiting_for_question.add(user_id)
        await message.answer(
            "✍️ Напишіть ваше питання.\n"
            "Модератор відповість вам особисто."
        )
        return

    # --- 2. КОРИСТУВАЧ ПИШЕ САМЕ ПИТАННЯ ---
    if user_id in waiting_for_question:
        waiting_for_question.remove(user_id)

        await bot.send_message(
            MODERATOR_ID,
            f"❓ ПИТАННЯ ВІД ГОСТЯ\n\n"
            f"{message.from_user.full_name}\n"
            f"(id: {user_id})\n\n"
            f"{text}\n\n"
            f"⬇️ Щоб відповісти гостю, натисніть REPLY на це повідомлення"
        )

        await message.answer("✅ Дякуємо! Питання передано модератору.")
        return

    # --- 3. КНОПКИ МЕНЮ ---
    if "Програма" in text:
        await message.answer_photo(FSInputFile("files/program.jpg"))
        return

    if "Точка" in text:
        await message.answer(f"📍 Локація заходу:\n{MAP_LINK}")
        return

    if "Корисна" in text:
        await message.answer(
            "Оберіть, будь ласка, що вас цікавить 👇",
            reply_markup=useful_keyboard
        )
        return

    # --- 4. ВІДПОВІДЬ МОДЕРАТОРА ЧЕРЕЗ REPLY ---
    if user_id == MODERATOR_ID and message.reply_to_message:
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

# ================== CALLBACKS ==================

@dp.callback_query(lambda c: c.data == "wine")
async def send_wine(call: types.CallbackQuery):
    await call.message.answer_document(FSInputFile("files/wine.pdf"))
    await call.answer()

@dp.callback_query(lambda c: c.data == "products")
async def send_products(call: types.CallbackQuery):
    await call.message.answer_document(FSInputFile("files/products.pdf"))
    await call.answer()

# ================== FLASK ==================

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
