from telebot import types


def category_keyboard(categories):
    """Генерит клавиатуры категорий/подкатегорий"""
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        print(category.slug)
        keyboard.add(types.InlineKeyboardButton(text=category.name, callback_data=category.slug))
    return keyboard


def product_keyboard(products):
    # Изменить модель и сделать одну клавиатуру
    """Генерит клавиатуру для товаров """
    keyboard = types.InlineKeyboardMarkup()
    for product in products:
        print(product.slug)
        keyboard.add(types.InlineKeyboardButton(text=product.title, callback_data=product.slug))
    return keyboard