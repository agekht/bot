import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from datetime import datetime, timezone

API_TOKEN = '7674009820:AAFUnpILU1xzJKtHn5-7wS3jWoG1Zcl6YDk'

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатуры
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="первую таблетку")],
        [KeyboardButton(text="вторую таблетку (вместе с остальными)")],
        [KeyboardButton(text="сбросить все")],
        [KeyboardButton(text="пока не пила (назад в меню)")]
    ],
    resize_keyboard=True
)

# Отмеченные таблетки
user_pills = {}

def get_user_data(user_id):
    if user_id not in user_pills:
        user_pills[user_id] = {"first": False, "second": False}
    return user_pills[user_id]

@dp.message(Command("start"))
async def start(message: types.Message):
    user_data = get_user_data(message.from_user.id)
    await message.answer("Ты выпила Велаксин?", reply_markup=keyboard)

@dp.message()
async def handle_buttons(message: types.Message):
    user_id = message.from_user.id
    user_data = get_user_data(user_id)
    text = message.text.lower()

    if "первую таблетку" in text or "уже выпила" in text:
        user_data["first"] = True
    elif "вторую таблетку" in text or "вместе с остаљными" in text:
        user_data["second"] = True
    elif "сбросить все" in text:
        user_data["first"] = False
        user_data["second"] = False
    
    date_today = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    status_message = (f"*{date_today}*\n"
                      f"Первая таблетка за сегодня: {'✅' if user_data['first'] else '❌'}\n"
                      f"Вторая таблетка за сегодня (и остаљные вместе с ней!): {'✅' if user_data['second'] else '❌'}\n"
                      "Не забудь отметиться, когда выпьешь следующую таблетку! ❤️")
    
    if user_data["first"] and user_data["second"]:
        status_message += "\n\n*Come back tomorrow, love!*"
    
    await message.answer(status_message, parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
