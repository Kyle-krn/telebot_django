import telebot
from main_app.models import *
from .handlers import bot
from django.db.models import Q
from main_app.management.commands.keyboards import *
from main_app.management.commands.utils import *
import requests



@bot.message_handler(regexp='^(Корзина)$')
@bot.callback_query_handler(func=lambda call: call.data == 'back_cart')
def cart_handlers(message):
    '''Главная страница корзины'''
    text = ''
    try:
        user_id = message.chat.id
    except AttributeError:  # Если юзер переходит по кнопке назад 
        bot.delete_message(message.message.chat.id, message.message.message_id)
        user_id = message.message.chat.id

    user = TelegramUser.objects.get(chat_id=user_id)
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    if PayProduct.objects.filter(user=user).delete()[0]:    # Добавляем забронированные товары обратно
        for item in cart:
            item.product.count += item.count
            item.product.save()

    for item in cart:   # Перепроверяем кол-во товара в корзине и сравниваем с кол-вом товара на складе
        if item.count > item.product.count:
            item.count = item.product.count
            item.save()
        if item.product.count <= 0:
            item.delete()

    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))   # Без этого запроса корзина не станет пустой если от туда удалится весь товар

    if not cart:    # Если корзина пустая
        text = '***Нет товаров в корзине***'
        return bot.send_message(chat_id=user_id, text=text, parse_mode='markdown')
        
    if not user.post_index:     # Если нет данных о доставке
        text += '***Вы не заполнили данные о доставке***\nЧто бы продолжить, заполните данные\n\n'
        keyboard = cart_keyboard()
    else:
        weight = sum([x.count * x.product.weight for x in cart])
        try:    # Пытаемся расчитать стоймость доставки
            delivery_pay = check_price_delivery(
                post_index=user.post_index, weight=weight)
            delivery_time = check_time_delivery(
                post_index=user.post_index, weight=weight)
        except:
            return bot.send_message(message.chat.id, 'При расчете стоймости доставки произошла ошибка')
            
        product_pay = sum([x.count * x.product.price for x in cart])    # Общая сумма корзины

        text += f'Стоймость доставки - {delivery_pay} руб.\nСтоймость товара - {product_pay} руб.\nОбщая стоймость - {float(delivery_pay)+float(product_pay)} руб.\nВремя доставки примерно {delivery_time} дней(дня)\n\n'
        keyboard = cart_keyboard(pay=delivery_pay)

    for item in cart:
        text += f'Товар - {item.product.title}\nКол-во {item.count} \n\n'

    bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard, parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'change_cart')
def change_cart_handlers(call):
    '''Изменить товары в корзине'''
    cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False))
    keyboard = change_cart_keyboard(cart=cart)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Выберите какой товар удалить из корзины', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'del')
def del_product_in_cart_handlers(call):
    '''Удалить определенный товар'''
    product_slug = call.data.split('~')[1]
    cart_product = TelegramProductCartCounter.objects.get(Q(user__chat_id=call.message.chat.id) & Q(counter=False) & Q(product__slug=product_slug))
    if call.data.split('~')[-1] == 'yes':
        cart_product.delete()
        return change_cart_handlers(call)
    elif call.data.split('~')[-1] == 'no':
        return change_cart_handlers(call)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f'Вы уверены что хотите удалить из корзины {cart_product.product.title}?', reply_markup=yes_no_keyboard(call.data))


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'del_all')
def del_all_product_in_cart_handlers(call):
    print(call.data)
    '''Удалить из корзины все'''
    if call.data.split('~')[-1] == 'yes':
        cart = TelegramProductCartCounter.objects.filter(
            Q(user__chat_id=call.message.chat.id) & Q(counter=False)).delete()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Корзина пуста', reply_markup=main_keyboard())

    elif call.data.split('~')[-1] == 'no':
        return change_cart_handlers(call)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text='Вы уверены что хотите удалить все из корзины?', reply_markup=yes_no_keyboard('del_all'))


