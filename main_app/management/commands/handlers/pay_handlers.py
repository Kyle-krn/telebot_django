from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from django.db.models import Q
import random
import string
import datetime

###///
#datetime.datetime.now(datetime.timezone.utc)

def generate_alphanum_random_string(length):
    """Генератор рандомных строк типа - s4Knf3Lf35"""
    letters_and_digits = string.ascii_letters + string.digits
    rand_string = ''.join(random.sample(letters_and_digits, length))
    return rand_string


@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'pay')
def pay_handlers(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    pay_word = generate_alphanum_random_string(6)
    delivery_pay = int(call.data.split('~')[1])
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    product_pay = sum([x.count * x.product.price for x in cart])
    pay_data = PayProduct.objects.create(user=user, pay_comment=pay_word, delivery_pay=delivery_pay, product_pay=product_pay)
    #### бронируем товар в каталоге
    for item in cart:
        print(item.product.count)
        item.product.count -= item.count
        print(item.product.count)
        item.product.save()

    text = f'Переведите на кошелек +79006292609 {delivery_pay+product_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_word}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())


@bot.callback_query_handler(func=lambda call: call.data == 'check_pay')
def check_pay_handlers(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    try:
        pay_data = PayProduct.objects.get(user__chat_id=call.message.chat.id)
    except PayProduct.DoesNotExist: 
        text = f'Ваша заявка была удалена по истичении времени\nЕсли вы оплатили, а ваша заяка удалилась, пожалуйста обратитесь к администратору - @здесь оставить контакт для связи'
        bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())
        return
    timenow = datetime.datetime.now(datetime.timezone.utc)
    time_passed = abs(int((pay_data.datetime - timenow).total_seconds() / 60))
    text = f'Прошло {time_passed} минут.\n\nПереведите на кошелек +79006292609 {pay_data.product_pay + pay_data.delivery_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_data.pay_comment}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())
