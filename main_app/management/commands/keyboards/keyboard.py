from telebot import types


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    product = types.KeyboardButton('💰 Каталог')
    keyboard.add(product)
    return keyboard