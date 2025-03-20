import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from aiogram.utils.markdown import hbold
from datetime import datetime, timezone, timedelta

API_TOKEN = "7674009820:AAFUnpILU1xzJKtHn5-7wS3jWoG1Zcl6YDk"

logging.basicConfig(level=logging.INFO)
bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Клавиатуры
keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="первую таблетку")],
        [KeyboardButton(text="вторую таблетку (вместе с остальными)")],
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
    elif "вторую таблетку" in text or "вместе с остальными" in text:
        user_data["second"] = True

    await message.answer(f"Отмечено: первая - {'✅' if user_data['first'] else '❌'}, вторая - {'✅' if user_data['second'] else '❌'}")

async def send_reminders():
    while True:
        now = datetime.now(timezone.utc)
        next_7am = now.replace(hour=7, minute=0, second=0, microsecond=0)
        next_12pm = now.replace(hour=12, minute=0, second=0, microsecond=0)

        if now >= next_7am:
            next_7am += timedelta(days=1)
        if now >= next_12pm:
            next_12pm += timedelta(days=1)

        wait_time = min((next_7am - now).total_seconds(), (next_12pm - now).total_seconds())
        await asyncio.sleep(wait_time)

        now = datetime.now(timezone.utc)
        for user_id, data in user_pills.items():
            if now.hour == 7 and not data["first"]:
                await bot.send_message(user_id, "Выпила первую таблетку?", reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="уже выпила, не отметила")], [KeyboardButton(text="нет, сейчас выпью")]],
                    resize_keyboard=True
                ))
            if now.hour == 12 and not data["second"]:
                await bot.send_message(user_id, "Выпила вторую таблетку?", reply_markup=ReplyKeyboardMarkup(
                    keyboard=[[KeyboardButton(text="уже выпила, не отметила")], [KeyboardButton(text="нет, сейчас выпью")]],
                    resize_keyboard=True
                ))

async def main():
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
