import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command
from datetime import datetime, timezone, timedelta

API_TOKEN = '7674009820:AAFUnpILU1xzJKtHn5-7wS3jWoG1Zcl6YDk'

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

    date_today = datetime.now(timezone.utc).strftime("%d.%m.%Y")
    status_message = (f"*{date_today}*\n"
                      f"Первая таблетка за сегодня: {'✅' if user_data['first'] else '❌'}\n"
                      f"Вторая таблетка за сегодня (и остальные вместе с ней!): {'✅' if user_data['second'] else '❌'}\n"
                      "Не забудь отметиться, когда выпьешь следующую таблетку! ❤️")
    
    await message.answer(status_message, parse_mode="Markdown")

async def send_reminders():
    while True:
        now = datetime.now(timezone.utc)

        # Укажи тестовое время, например, через 3 минуты
        next_7am = now.replace(hour=5, minute=59, second=0, microsecond=0)
        next_12pm = now.replace(hour=6, minute=0, second=0, microsecond=0)

        # Увеличиваем на 1 день, если время уже прошло
        if now >= next_7am:
            next_7am += timedelta(days=1)
        if now >= next_12pm:
            next_12pm += timedelta(days=1)

        while True:
            now = datetime.now(timezone.utc)

            if now >= next_7am:
                for user_id, data in user_pills.items():
                    if not data["first"]:
                        logging.info(f"Отправка утреннего уведомления пользователю {user_id}")
                        await bot.send_message(user_id, "Выпила первую таблетку?", reply_markup=ReplyKeyboardMarkup(
                            keyboard=[[KeyboardButton(text="уже выпила, не отметила")], [KeyboardButton(text="нет, сейчас выпью")]],
                            resize_keyboard=True
                        ))
                next_7am += timedelta(days=1)  # Переносим следующее уведомление на завтра

            if now >= next_12pm:
                for user_id, data in user_pills.items():
                    if not data["second"]:
                        logging.info(f"Отправка дневного уведомления пользователю {user_id}")
                        await bot.send_message(user_id, "Выпила вторую таблетку?", reply_markup=ReplyKeyboardMarkup(
                            keyboard=[[KeyboardButton(text="уже выпила, не отметила")], [KeyboardButton(text="нет, сейчас выпью")]],
                            resize_keyboard=True
                        ))
                next_12pm += timedelta(days=1)  # Переносим следующее уведомление на завтра

            await asyncio.sleep(60)  # Проверяем каждую минуту


async def main():
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
