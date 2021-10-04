from telebot import types


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = types.KeyboardButton('💰 Каталог')
    button1 = types.KeyboardButton('Корзина')
    button1 = types.KeyboardButton('Данные о доставке')
    keyboard.add(button)
    keyboard.add(button1)
    return keyboard

    