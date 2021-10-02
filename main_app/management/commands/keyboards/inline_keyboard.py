from telebot import types


def category_keyboard(categories):
    """Генерит клавиатуры главных катеогрий 2ух типов"""
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        print(category.slug)
        keyboard.add(types.InlineKeyboardButton(text=category.name, callback_data=category.slug))
    return keyboard