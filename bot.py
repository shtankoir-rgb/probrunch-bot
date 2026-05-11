import asyncio
import os
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile
)

# ================= НАСТРОЙКИ =================

BOT_TOKEN = os.getenv("BOT_TOKEN")           # токен від BotFather
MODERATOR_ID = (os.getenv("MODERATOR_ID"))  # Telegram ID модератора

MAP_LINK = "https://maps.app.goo.gl/d5cZUQbqf8exr11X7"

# ================= ІНІЦІАЛІЗАЦІЯ =================

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

waiting_for_question = set()

# ================= КЛАВІАТУРИ =================

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

# ================= /START =================

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        "Вітаємо у чат-боті PRO BRUNCH від METRO 🍷\n\n"
        "Раді бачити вас серед гостей нашого бранчу!\n\n"
        "Тут ви знайдете:\n"
        "• програму вечора\n"
        "• точку локації на мапі\n"
        "• корисну інформацію\n\n"
        "А якщо у вас виникнуть будь-які запитання —\n"
        "просто натисніть «❓ Питання / відповіді»,\n"
        "і ми з радістю допоможемо.\n\n"
        "До зустрічі на PRO BRUNCH ✨",
        reply_markup=main_keyboard
    )

    await message.answer_photo(
        FSInputFile("files/invitation.jpg")
    )

# ================= ОСНОВНА ЛОГІКА =================

@dp.message()
async def handle_messages(message: types.Message):
    user_id = message.from_user.id
    text = message.text

    # ---------- ГОСТІ ----------
    if user_id != MODERATOR_ID:

        if text == "❓ Питання / відповіді":
            waiting_for_question.add(user_id)
            await message.answer(
                "Напишіть ваше питання ✍️\n"
                "Модератор відповість вам особисто."
            )

        elif user_id in waiting_for_question:
            waiting_for_question.remove(user_id)
            await bot.send_message(
                MODERATOR_ID,
                f"❓ Питання від:\n"
                f"{message.from_user.full_name}\n"
                f"(id: {user_id})\n\n"
                f"{text}"
            )
            await message.answer("✅ Дякуємо! Питання передано модератору.")

        elif text == "📄 Програма":
            await message.answer_document(
                FSInputFile("files/program.pdf")
            )

        elif text == "📍 Точка на мапі":
            await message.answer(
                f"📍 Локація заходу:\n{MAP_LINK}"
            )

        elif text == "🍷 Корисна інформація":
            await message.answer(
                "Оберіть, будь ласка, що вас цікавить 👇",
                reply_markup=useful_keyboard
            )

    # ---------- МОДЕРАТОР ----------
    else:
        if message.reply_to_message and "id:" in message.reply_to_message.text:
            try:
                user_id = int(
                    message.reply_to_message.text
                    .split("id:")[1]
                    .split(")")[0]
                )
                await bot.send_message(
                    user_id,
                    f"💬 Відповідь модератора:\n\n{message.text}"
                )
            except:
                pass

# ================= CALLBACKS =================

@dp.callback_query(lambda c: c.data == "wine")
async def send_wine(call: types.CallbackQuery):
    await call.message.answer_document(
        FSInputFile("files/wine.pdf")
    )
    await call.answer()

@dp.callback_query(lambda c: c.data == "products")
async def send_products(call: types.CallbackQuery):
    await call.message.answer_document(
        FSInputFile("files/products.pdf")
    )
    await call.answer()

# ================= ЗАПУСК =================

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
