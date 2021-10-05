from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from django.db.models import Q
from main_app.management.commands.utils import *
import datetime

###///
#datetime.datetime.now(datetime.timezone.utc)


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'pay')
def pay_handlers(call):
    '''Переход на кнопку - оплатить'''
    pay_word = generate_alphanum_random_string(6)
    delivery_pay = int(call.data.split('~')[1])
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    product_pay = sum([x.count * x.product.price for x in cart])
    pay_data = PayProduct.objects.create(user=user, pay_comment=pay_word, delivery_pay=delivery_pay, product_pay=product_pay)
    for item in cart: # бронируем товар в каталоге
        item.product.count -= item.count
        item.product.save()
    text = f'Переведите на кошелек +79006292609 {delivery_pay+product_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_word}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=text, reply_markup=check_pay_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'check_pay')
def check_pay_handlers(call):
    '''Проверка оплаты'''
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    try:
        pay_data = PayProduct.objects.get(user__chat_id=call.message.chat.id)
    except PayProduct.DoesNotExist: 
        text = f'Ваша заявка была удалена по истичении времени\nЕсли вы оплатили, а ваша заяка удалилась, пожалуйста обратитесь к администратору - @здесь оставить контакт для связи'
        bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())
        return

    if check_qiwi(comment=pay_data.pay_comment, price=(pay_data.delivery_pay+pay_data.product_pay)):
        bot.send_message(chat_id=call.message.chat.id, text='Ваш заказ принят!')
        user = TelegramUser.objects.get(chat_id=call.message.chat.id)
        sold_product(user, pay_data)
        return
    timenow = datetime.datetime.now(datetime.timezone.utc)
    time_passed = abs(int((pay_data.datetime - timenow).total_seconds() / 60))
    text = f'Прошло {time_passed} минут.\n\nПереведите на кошелек +79006292609 {pay_data.product_pay + pay_data.delivery_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_data.pay_comment}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())


def sold_product(user, pay_data):
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    for item in cart:
        SoldProduct.objects.create(user=user, product=item.product, price=item.product.price*item.count, delivery_pay=pay_data.delivery_pay, count=item.count)
    pay_data.delete()
    cart.delete()
    
