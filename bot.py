import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from datetime import datetime

# Токен бота (замени на свой)
API_TOKEN = "7674009820:AAFUnpILU1xzJKtHn5-7wS3jWoG1Zcl6YDk"

# Включаем логирование
logging.basicConfig(level=logging.INFO)

# Создаем объекты бота и диспетчера
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

# Храним состояние таблеток в памяти (для простоты, можно заменить на базу данных)
pills_taken = {}

# Клавиатура с вариантами ответов
keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(KeyboardButton("первую таблетку"))
keyboard.add(KeyboardButton("вторую таблетку (вместе с остальными)"))
keyboard.add(KeyboardButton("пока не пила (назад в меню)"))

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    user_id = message.from_user.id
    pills_taken[user_id] = {"first": False, "second": False}
    await message.answer("Привет! Ты сегодня выпила Велаксин?", reply_markup=keyboard)

@dp.message_handler(lambda message: message.text in ["первую таблетку", "вторую таблетку (вместе с остальными)"])
async def take_pill(message: types.Message):
    user_id = message.from_user.id
    if user_id not in pills_taken:
        pills_taken[user_id] = {"first": False, "second": False}
    
    if message.text == "первую таблетку":
        pills_taken[user_id]["first"] = True
    elif message.text == "вторую таблетку (вместе с остальными)":
        pills_taken[user_id]["second"] = True
    
    # Формируем сообщение с отметками
    date_today = datetime.now().strftime("%d.%m.%Y")
    first_status = "✅" if pills_taken[user_id]["first"] else "❌"
    second_status = "✅" if pills_taken[user_id]["second"] else "❌"
    response = f"*{date_today}*\nПервая таблетка за сегодня: {first_status}\nВторая таблетка за сегодня (и остальные вместе с ней!): {second_status}\nНе забудь отметиться, когда выпьешь следующую таблетку! ❤️"
    
    if pills_taken[user_id]["first"] and pills_taken[user_id]["second"]:
        response += "\nТы восхитительна! Come back tomorrow, love"
    
    await message.answer(response, parse_mode="Markdown")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
