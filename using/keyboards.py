from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardMarkup, InlineKeyboardButton

get_checkpoints = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Показать список остановок')],
],
    resize_keyboard=True,
    input_field_placeholder='Остановка') #клавиатура

get_checkpoints_back = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Показать список остановок (обратный рейс)')],
],
    resize_keyboard=True,
    input_field_placeholder='Остановка')

get_checkpoints_back_plus = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text='Обратный рейс')],
    [KeyboardButton(text='Меню')],],
    resize_keyboard = True,
    input_field_placeholder = 'Выбор',
)

abilities_arr = ['Ближайшие рейсы', 'Оповещение по времени', 'Расписание', "Список остановок"]
async def abilities():
    keyboard = ReplyKeyboardBuilder()
    for ability in abilities_arr:
        keyboard.add(KeyboardButton(text=ability))
    keyboard.resize_keyboard = True
    keyboard.input_field_placeholder = 'Возможности бота'
    return keyboard.adjust(2).as_markup()