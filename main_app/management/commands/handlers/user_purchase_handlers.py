from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from vape_shop.settings import DADATA_TOKEN
from dadata import Dadata
from django.db.models import Q


@bot.message_handler(regexp='^(📂 Мои товары)$')
def my_purchase_handlers(message):
    order_product_queryset = OrderingProduct.objects.filter(user__chat_id=message.chat.id)
    data = message.chat
    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })
    if not order_product_queryset:
        text = 'У вас еще нет покупок'
        return bot.send_message(chat_id=message.chat.id, text=text)
    bot.send_message(chat_id=message.chat.id, text='Для просмотра трек-номера выберите нужный товар:', reply_markup=purchase_keyboard(order_product_queryset))


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'sp')
def track_code_handlers(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    try:
        pk = call.data.split('~')[1]
        order_product = OrderingProduct.objects.get(Q(user__chat_id=call.message.chat.id) & Q(pk=pk))
        if order_product.payment_bool == False:
            return bot.send_message(chat_id=call.message.chat.id, text='Вы не оплатили заказ, пожалуйста, свяжитесь с нашим менеджером @kyle_krn', reply_markup=manager_keyboard())
    except:
        return bot.send_message(chat_id=call.message.chat.id, text='Ваш неоплаченный заказ был удален')
    text = ''
    for item in order_product.soldproduct_set.all():
        text += f'***Товар -*** {item.product.title}\n***Количество -*** {item.count} шт.\n\n'
    
    if not order_product.track_code:
        text += 'У вашего заказа пока нет трек номера, но совсем скоро он здесь появится'

    else:
        text += f'***Трек номер вашего заказа -*** {order_product.track_code}'
    bot.send_message(chat_id=call.message.chat.id, text=text, parse_mode='markdown')