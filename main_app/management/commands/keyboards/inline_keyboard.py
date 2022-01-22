from telebot import types
from main_app.models import QiwiToken


def category_keyboard(categories, back=False):
    """Генерит клавиатуры категорий/подкатегорий"""
    keyboard = types.InlineKeyboardMarkup()
    for category in categories:
        keyboard.add(types.InlineKeyboardButton(text=category.name, callback_data=category.pk_for_telegram))
    if back:
        keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'back_cat~'))
    return keyboard


def product_keyboard(sub_slug, products, search=False, back=True):
    # Изменить модель и сделать одну клавиатуру
    """Генерит клавиатуру для товаров """
    keyboard = types.InlineKeyboardMarkup()
    for product in products:
        if not search:
            keyboard.add(types.InlineKeyboardButton(text=product.title, callback_data=product.pk_for_telegram))
        else:
            keyboard.add(types.InlineKeyboardButton(text=product.title, callback_data=f"search_p~{product.pk_for_telegram}"))

    keyboard.add(types.InlineKeyboardButton(text='Назад', callback_data=f'{sub_slug}'))
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
    back_button = types.InlineKeyboardButton(text='<< Назад', callback_data=f'{subcat_slug}')
    keyboard.add(down_1, count, up_1)
    keyboard.add(down_10, up_10)
    keyboard.add(buy)
    keyboard.add(back_button)
    return keyboard

def cart_keyboard(pay=None):
    keyboard = types.InlineKeyboardMarkup()
    if pay:
        if QiwiToken.objects.filter(active=True):
            keyboard.add(types.InlineKeyboardButton(text='Оплатить через Qiwi', callback_data=f'pay~{pay}'))
        keyboard.add(types.InlineKeyboardButton(text='Оформить заказ', callback_data=f'new_order~{pay}'))
    else:
        keyboard.add(types.InlineKeyboardButton(text='Заполнить данные для доставки', callback_data='new_delivery_data'))
    button = types.InlineKeyboardButton(text='Изменить корзину', callback_data='change_cart')
    keyboard.add(button)
    return keyboard

def change_cart_keyboard(cart):
    keyboard = types.InlineKeyboardMarkup()
    for item in cart:
        keyboard.add(types.InlineKeyboardButton(text=f'{item.product.title}', callback_data=f'del~{item.product.pk_for_telegram}'))
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
        keyboard.add(types.InlineKeyboardButton(text=item.name, callback_data=f'search~{item.pk_for_telegram}'))
    return keyboard


def check_pay_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Проверить оплату', callback_data='check_pay'))
    keyboard.add(types.InlineKeyboardButton(text='Отменить оплату', callback_data='cancel_pay'))
    return keyboard

def purchase_keyboard(soldproduct):
    keyboard = types.InlineKeyboardMarkup()
    for item in soldproduct:
        keyboard.add(types.InlineKeyboardButton(text=f"От {item.datetime.strftime('%m/%d/%Y')} на сумму {item.price} руб.", callback_data=f'sp~{item.pk}'))
    return keyboard

def manager_keyboard():
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(types.InlineKeyboardButton(text='Связаться с нашим менеджером', url='https://t.me/kyle_krn'))
    return keyboard