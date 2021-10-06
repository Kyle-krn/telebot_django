from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from vape_shop.settings import DADATA_TOKEN
from dadata import Dadata
from django.db.models import Q


@bot.message_handler(regexp='^(Мои товары)$')
def my_purchase_handlers(message):
    order_product_queryset = OrderingProduct.objects.filter(user__chat_id=message.chat.id)
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
    except:
        return bot.send_message(chat_id=call.message.chat.id, text='Что то пошло не так')
    text = ''
    for item in order_product.sold_product.all():
        text += f'Товар - {item.product.title}\nКоличество - {item.count}\n\n'
    
    if not order_product.track_code:
        text += 'У вашего заказа пока нет трек номера, но совсем скоро он здесь появится'

    else:
        text += f'Трек номер вашего заказа - {order_product.track_code}'
    bot.send_message(chat_id=call.message.chat.id, text=text)