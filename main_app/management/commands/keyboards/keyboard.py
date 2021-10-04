from telebot import types


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('💰 Каталог')
    button1 = types.KeyboardButton('Корзина')
    button2 = types.KeyboardButton('Данные о доставке')
    keyboard.add(button)
    keyboard.add(button1)
    keyboard.add(button2)
    return keyboard

    