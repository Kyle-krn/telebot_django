from .handlers import bot
from django.db.models import Q
from main_app.models import *
from main_app.management.commands.keyboards import *
from vape_shop.settings import TELEGRAM_GROUP_ID


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'new_order')
def new_order(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)    
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    delivery_pay = int(call.data.split('~')[1])
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    order = OrderingProduct.objects.create(user=user, delivery_pay=delivery_pay, fio=user.fio, address=user.address, number=user.number, post_index=user.post_index)
    for item in cart:
        order_product = SoldProduct.objects.create(product=item.product, count=item.count, price=item.product.price, order=order)
    order.set_order_price()
    cart.delete()
    # bot.send_message(chat_id=TELEGRAM_GROUP_ID, text=f'Сделан заказ через менедежра на сумму {delivery_pay+sum([x.count * x.product.price for x in cart])} руб.')
    bot.send_message(chat_id=call.message.chat.id, text='Спасибо за заказ! Пожалуйста свяжитесь с нашим менеджером по адресу @kyle_krn для оплаты.', reply_markup=manager_keyboard())
