import telebot
from main_app.models import *
from .handlers import bot
from django.db.models import Q
from main_app.management.commands.keyboards import *


@bot.message_handler(regexp='^(Корзина)$')
@bot.callback_query_handler(func=lambda call: call.data == 'back_cart')
def cart_handlers(message):
    text = '' 
    try:
        user_id = message.chat.id
    except:
        bot.delete_message(message.message.chat.id, message.message.message_id)
        user_id = message.message.chat.id
    user = TelegramUser.objects.get(chat_id=user_id) 
    if not user.post_index:
        text += '***Вы не заполнили данные о доставке***\nЧто бы продолжить, заполните данные\n\n' 
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    if not cart:
        text = '***Нет товаров в корзине***'
        bot.send_message(chat_id=user_id, text=text, parse_mode='markdown')
        return
    else:
        for item in cart:
            text += f'Товар - {item.product.title}\nКол-во {item.count} \n\n'
    keyboard = cart_keyboard()
    bot.send_message(chat_id=user_id, text=text, reply_markup=keyboard, parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'change_cart')
def change_cart_handlers(call):
    # bot.delete_message(call.message.chat.id, call.message.message_id)
    cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False))
    keyboard = change_cart_keyboard(cart=cart)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Выберите какой товар удалить из корзины', reply_markup=keyboard)
    

@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'del')
def del_product_in_cart_handlers(call):
    # bot.delete_message(call.message.chat.id, call.message.message_id)
    product_slug = call.data.split('~')[1]
    cart_product = TelegramProductCartCounter.objects.get(Q(user__chat_id=call.message.chat.id) & Q(counter=False) & Q(product__slug=product_slug))
    if call.data.split('~')[-1] == 'yes':
        cart_product.delete()
        return change_cart_handlers(call)
    elif call.data.split('~')[-1] == 'no':
        return change_cart_handlers(call)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'Вы уверены что хотите удалить из корзины {cart_product}?', reply_markup=yes_no_keyboard(call.data))
    # bot.change_message


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'del_all')
def del_all_product_in_cart_handlers(call):
    if call.data.split('~')[-1] == 'yes':
        cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False)).delete()
        bot.delete_message(call.message.chat.id, call.message.message_id)
        bot.send_message(call.message.chat.id, 'Корзина успешно очищена', reply_markup=main_keyboard())
        return
    elif call.data.split('~')[-1] == 'no':
        return change_cart_handlers(call)
    # bot.delete_message(call.message.chat.id, call.message.message_id)
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text='Вы уверены что хотите удалить все из корзины?', reply_markup=yes_no_keyboard('del_all'))
    