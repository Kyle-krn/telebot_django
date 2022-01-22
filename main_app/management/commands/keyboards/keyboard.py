from telebot import types

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('💰 Каталог')
    button1 = types.KeyboardButton('🛒 Корзина')
    button2 = types.KeyboardButton('📦 Данные для доставки')
    button3 = types.KeyboardButton('🔎 Поиск товаров')
    button4 = types.KeyboardButton('📂 Мои товары')
    keyboard.add(button, button1)
    keyboard.add(button2, button3)
    keyboard.add(button4)
    return keyboard

    