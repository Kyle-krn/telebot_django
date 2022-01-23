from main_app.models import *
from bot.management.commands.keyboards import *
from vape_shop.settings import DADATA_TOKEN
from .handlers import bot
from dadata import Dadata

dadata = Dadata(DADATA_TOKEN)


@bot.callback_query_handler(func=lambda call: call.data == 'stop_next_step')
def stop_next_step_handlers(call):
    user = TelegramUser.objects.get(chat_id=call.message.chat.id)
    user.post_index = None
    user.address = None
    user.fio = None
    user.number = None
    user.save()
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.message_handler(regexp='^(📦 Данные для доставки)$')
def post_data(message):
    try:
        user = TelegramUser.objects.get(chat_id=message.chat.id)
    except TelegramUser.DoesNotExist:
        bot.send_message(chat_id=message.chat.id, text='Упс что то пошло не так')
        return

    data = message.chat
    TelegramUser.objects.get_or_create(chat_id=data.id,
                                       defaults={
                                           'first_name': data.first_name,
                                           'last_name': data.last_name,
                                           'username': data.username
                                       })
        
    if not user.post_index:
        message = bot.send_message(message.chat.id, f"Укажите ваш индекс: ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_index)
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Введенные данные:\n***Индекс -*** {user.post_index}\n\n***Адрес -*** {user.address}\n\n***ФИО -*** {user.fio}\n\n***Номер телефона -*** {user.number}', reply_markup=edit_delivery_data_keyboard(), parse_mode='markdown')


@bot.callback_query_handler(func=lambda call: call.data == 'new_delivery_data')
def new_delivery_data_handlers(call):
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    message = bot.send_message(call.message.chat.id, f"Укажите ваш индекс: ", reply_markup=cancel_next_step_keyboard())
    bot.register_next_step_handler(message, input_index)



def input_index(message):
    try:
        post_index = int(message.text)
    except ValueError:
        message = bot.send_message(message.chat.id, f"Укажите ваш индекс(только цифры): ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_index)
        return

    result = dadata.find_by_id("postal_office", post_index)
    if result:
        user = TelegramUser.objects.get(chat_id=message.chat.id)
        user.post_index = post_index
        user.save()

        message = bot.send_message(message.chat.id, f"Введите адрес доставки (В формате: область, город, улица, дом ): ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_address)

    else:
        message = bot.send_message(message.chat.id, f"Введите настоящий индекс(только цифры): ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_index)
        return

def input_address(message):
    address = message.text
    if not address:
        message = bot.send_message(message.chat.id, f"Введите адрес доставки (В формате: область, город, улица, дом ): ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_address)
        return
    user = TelegramUser.objects.get(chat_id=message.chat.id)
    user.address = address
    user.save()
    message = bot.send_message(message.chat.id, f"Введите вашу фамилию, имя и отчество: ", reply_markup=cancel_next_step_keyboard())
    bot.register_next_step_handler(message, input_fio)


def input_fio(message):
    fio = message.text
    if not fio:
        message = bot.send_message(message.chat.id, f"Введите вашу фамилию, имя и отчество: ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_fio)
        return
    user = TelegramUser.objects.get(chat_id=message.chat.id)
    user.fio = fio
    user.save()
    message = bot.send_message(message.chat.id, f"Введите номер телефона (11 цифр без пробелов, начиная с 7): ", reply_markup=cancel_next_step_keyboard())
    bot.register_next_step_handler(message, input_phone)


def input_phone(message):
    try:
        phone = int(message.text)
        if len(str(phone)) != 11:
            message = bot.send_message(message.chat.id, f"Введите номер телефона (11 цифр без пробелов, начиная с 7): ", reply_markup=cancel_next_step_keyboard())
            bot.register_next_step_handler(message, input_phone)
            return
    except ValueError:
        message = bot.send_message(message.chat.id, f"Введите номер телефона (11 цифр без пробелов, начиная с 7): ", reply_markup=cancel_next_step_keyboard())
        bot.register_next_step_handler(message, input_phone)
        return
    user = TelegramUser.objects.get(chat_id=message.chat.id)
    user.number = phone
    user.save()
    bot.clear_step_handler_by_chat_id(chat_id=message.chat.id)
    bot.send_message(chat_id=message.chat.id, text='Данные о доставке успешно добавлены')
