from telebot import types


def category_keyboard(categories, back=False):
    """Генерит клавиатуры категорий/подкатегорий"""
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category.name, callback_data=category.slug))
    if back:
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_cat~'))
    return keyboard


def product_keyboard(sub_slug,products):
    # Изменить модель и сделать одну клавиатуру
    """Генерит клавиатуру для товаров """
    keyboard = types.InlineKeyboardMarkup()
    for product in products:
        keyboard.add(types.InlineKeyboardButton(text=product.title, callback_data=product.slug))
    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_sub~{sub_slug}'))
    return keyboard


def buy_keyboard(subcat_slug,slug, count):
    '''Клавиатура покупки'''
    keyboard = types.InlineKeyboardMarkup()
    down_1 = types.InlineKeyboardButton(text=f'🔻', callback_data=f'buy~{slug}~-1')
    count = types.InlineKeyboardButton(text=f'{count} шт', callback_data=f'buy~{slug}~0')
    up_1 = types.InlineKeyboardButton(text=f'🔺', callback_data=f'buy~{slug}~1')
    down_10 = types.InlineKeyboardButton(text=f'10 🔻', callback_data=f'buy~{slug}~-10')
    up_10 = types.InlineKeyboardButton(text=f'10 🔺', callback_data=f'buy~{slug}~10')
    buy = types.InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_cart')  # Изменить callback
    back_button = types.InlineKeyboardButton(text='<< Назад', callback_data=f'back_prod~{subcat_slug}')
    keyboard.add(down_1, count, up_1)
    keyboard.add(down_10, up_10)
    keyboard.add(buy)
    keyboard.add(back_button)
    return keyboard