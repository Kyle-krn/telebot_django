from telebot import types


def category_keyboard(categories, back=False):
    """Генерит клавиатуры категорий/подкатегорий"""
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category.name, callback_data=category.slug))
    if back:
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_cat~'))
    return keyboard


def product_keyboard(sub_slug,products, back=True):
    # Изменить модель и сделать одну клавиатуру
    """Генерит клавиатуру для товаров """
    keyboard = types.InlineKeyboardMarkup()
    for product in products:
        keyboard.add(types.InlineKeyboardButton(text=product.title, callback_data=product.slug))
    if back:
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_sub~{sub_slug}'))
    return keyboard


def buy_keyboard(subcat_slug,slug, count):
    '''Клавиатура покупки'''
    keyboard = types.InlineKeyboardMarkup()
    down_1 = types.InlineKeyboardButton(text=f'🔻', callback_data=f'buy~{slug}~-1')
    count = types.InlineKeyboardButton(text=f'{count} шт', callback_data=f'buy~{slug}~0')
    up_1 = types.InlineKeyboardButton(text=f'🔺', callback_data=f'buy~{slug}~1')
    down_10 = types.InlineKeyboardButton(text=f'5 🔻', callback_data=f'buy~{slug}~-5')
    up_10 = types.InlineKeyboardButton(text=f'5 🔺', callback_data=f'buy~{slug}~5')
    buy = types.InlineKeyboardButton(text=f'Купить', callback_data=f'add_to_cart')  # Изменить callback
    back_button = types.InlineKeyboardButton(text='<< Назад', callback_data=f'back_prod~{subcat_slug}')
    keyboard.add(down_1, count, up_1)
    keyboard.add(down_10, up_10)
    keyboard.add(buy)
    keyboard.add(back_button)
    return keyboard

def cart_keyboard(pay=None):
    keyboard = types.InlineKeyboardMarkup()
    if pay:
        keyboard.add(types.InlineKeyboardButton(text='Оплатить', callback_data=f'pay~{pay}'))
    button = types.InlineKeyboardButton(text='Изменить корзину', callback_data='change_cart')
    keyboard.add(button)
    return keyboard

def change_cart_keyboard(cart):
    keyboard = types.InlineKeyboardMarkup()
    for item in cart:
        keyboard.add(types.InlineKeyboardButton(text=f'{item.product.title}', callback_data=f'del~{item.product.slug}'))
    keyboard.add(types.InlineKeyboardButton(text=f'Удалить все', callback_data=f'del_all~'))
    keyboard.add(types.InlineKeyboardButton(text=f'Назад', callback_data=f'back_cart'))
    return keyboard

def yes_no_keyboard(callback):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Да', callback_data=f'{callback}~yes'))
    keyboard.add(types.InlineKeyboardButton(text='Нет', callback_data=f'{callback}~no'))
    return keyboard

def cancel_next_step_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Отменить', callback_data=f'stop_next_step'))
    return keyboard

def edit_delivery_data_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Ввести новые данные', callback_data='new_delivery_data'))
    return keyboard


def search_category_keyboard(categories):
    keyboard = types.InlineKeyboardMarkup()
    for item in categories:
        keyboard.add(types.InlineKeyboardButton(text=item.name, callback_data=f'search~{item.slug}'))
    return keyboard