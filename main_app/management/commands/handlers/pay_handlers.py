from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from django.db.models import Q
from main_app.management.commands.utils import *
import datetime

###///
#datetime.datetime.now(datetime.timezone.utc)

@bot.callback_query_handler(func=lambda call: call.data == 'cancel_pay')
def cancel_pay_handlers(call):
    '''Отмена брони и оплаты'''
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    cart = TelegramProductCartCounter.objects.filter(Q(user__chat_id=call.message.chat.id) & Q(counter=False))
    if PayProduct.objects.filter(user__chat_id=call.message.chat.id).delete()[0]:    # Добавляем забронированные товары обратно
        for item in cart:
            item.product.count += item.count
            item.product.save()
    bot.send_message(chat_id=call.message.chat.id, text='Бронь отменена')



@bot.callback_query_handler(func=lambda call: call.data.split('~')[0] == 'pay')
def pay_handlers(call):
    '''Переход на кнопку - оплатить'''
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    qiwi = QiwiToken.objects.get(active=True)   # Получаем активный токен
    try:
        balance = get_qiwi_balance(str(qiwi.number), str(qiwi.token))
        qiwi.balance = balance
        qiwi.save() 
        # Сделать отправку уведомления о том что токен не работает
    except:
        qiwi.blocked = True
        qiwi.active = False
        qiwi.save()
        return bot.send_message(chat_id=call.message.chat.id, text='К сожалению в данный момент оплата QIWI невозможна')
    
    pay_word = generate_alphanum_random_string(6)   # Генерим платежный комент
    delivery_pay = int(call.data.split('~')[1]) # Стоймость доставки
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))   # Получаем корзину юзера
    product_pay = sum([x.count * x.product.price for x in cart])    # Стоймость товара
    pay_data = PayProduct.objects.create(user=user, pay_comment=pay_word, delivery_pay=delivery_pay, product_pay=product_pay)   # Создаем модель оплаты
    for item in cart: # бронируем товар в каталоге
        item.product.count -= item.count
        item.product.save()
    text = f'Переведите на кошелек +{qiwi.number} {delivery_pay+product_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_word}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    message = bot.send_message(chat_id=call.message.chat.id,
                          text=text, reply_markup=check_pay_keyboard())
    bot.register_next_step_handler(message, check_pay_next_handler)



def check_pay_next_handler(message):
    '''Проверка оплаты - next_handlers'''
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
    bot.delete_message(chat_id=message.chat.id, message_id=message.message_id-1)
    try:
        pay_data = PayProduct.objects.get(user__chat_id=message.chat.id)
    except PayProduct.DoesNotExist: 
        text = f'Ваша заявка была удалена по истичении времени\nЕсли вы оплатили, а ваша заяка удалилась, пожалуйста обратитесь к администратору - @здесь оставить контакт для связи'
        bot.send_message(chat_id=message.chat.id, text=text, reply_markup=check_pay_keyboard())
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        return

    answer = check_qiwi(comment=pay_data.pay_comment, price=(pay_data.delivery_pay+pay_data.product_pay))
    qiwi = QiwiToken.objects.get(active=True)
    
    if answer:
        if answer == 'error':
            qiwi.blocked = True
            qiwi.active = False
            qiwi.save()
            return bot.send_message(chat_id=message.chat.id, text='К сожалению в данный момент оплата QIWI невозможна')

        bot.send_message(chat_id=message.chat.id, text='Ваш заказ принят!')
        user = TelegramUser.objects.get(chat_id=message.chat.id)
        bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
        sold_product(user, pay_data)
        return
    timenow = datetime.datetime.now(datetime.timezone.utc)
    
    time_passed = abs(int((pay_data.datetime - timenow).total_seconds() / 60))
    text = f'Прошло {time_passed} минут.\n\nПереведите на кошелек +{qiwi.number} {pay_data.product_pay + pay_data.delivery_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_data.pay_comment}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    message = bot.send_message(chat_id=message.chat.id, text=text, reply_markup=check_pay_keyboard())
    bot.register_next_step_handler(message, check_pay_next_handler)



@bot.callback_query_handler(func=lambda call: call.data == 'check_pay')
def check_pay_handlers(call):
    '''Проверка оплаты - inline'''
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    try:
        pay_data = PayProduct.objects.get(user__chat_id=call.message.chat.id)
    except PayProduct.DoesNotExist: 
        text = f'Ваша заявка была удалена по истичении времени\nЕсли вы оплатили, а ваша заяка удалилась, пожалуйста обратитесь к администратору - @здесь оставить контакт для связи'
        bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        return

    answer = check_qiwi(comment=pay_data.pay_comment, price=(pay_data.delivery_pay+pay_data.product_pay))
    qiwi = QiwiToken.objects.get(active=True)
    if answer:
        if answer == 'error':   
            qiwi.blocked = True
            qiwi.active = False
            qiwi.save()
            bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
            return bot.send_message(chat_id=call.message.chat.id, text='К сожалению в данный момент оплата QIWI невозможна ')
        bot.send_message(chat_id=call.message.chat.id, text='Ваш заказ принят!')
        user = TelegramUser.objects.get(chat_id=call.message.chat.id)
        bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
        sold_product(user, pay_data)
        return

    timenow = datetime.datetime.now(datetime.timezone.utc)
    
    time_passed = abs(int((pay_data.datetime - timenow).total_seconds() / 60))
    text = f'Прошло {time_passed} минут.\n\nПереведите на кошелек +{qiwi.number} {pay_data.product_pay + pay_data.delivery_pay} руб.\nОБЯЗАТЕЛЬНО УКАЖИТЕ В КОМЕНТАРИИ\n {pay_data.pay_comment}\n\nТовар забронирован на 15 минут для оплаты, если вы хотите отменить заявку, перейдите снова в корзину'
    bot.send_message(chat_id=call.message.chat.id, text=text, reply_markup=check_pay_keyboard())


def sold_product(user, pay_data):
    '''Успешная оплата'''
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    order = OrderingProduct.objects.create(user=user, delivery_pay=pay_data.delivery_pay, fio=user.fio, address=user.address, number=user.number, post_index=user.post_index)
    for item in cart:
        sold_product = SoldProduct.objects.create(product=item.product, price=item.product.price, count=item.count)
        order.sold_product.add(sold_product)
    order.save()
    pay_data.delete()
    cart.delete()
    
