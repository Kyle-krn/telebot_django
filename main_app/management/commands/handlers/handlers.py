import telebot
from main_app.models import *
from main_app.management.commands.keyboards.keyboard import *
from main_app.management.commands.keyboards.inline_keyboard import *


TELEGRAM_TOKEN = '2049844837:AAH-f33he41frWIkFqfV78t5f445DhtUHNk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)
category_list = [x.slug for x in Category.objects.all()] 


@bot.message_handler(regexp='^(💰 Каталог)$')
def catalog(message):
    categories = Category.objects.all()
    bot.send_message(message.chat.id, f'Выбирай', reply_markup=category_keyboard(categories))


@bot.callback_query_handler(func=lambda call: call.data in category_list)
def category(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    try:
        category = Category.objects.get(slug=call.data)
        print(category.photo.url)
    except:
        bot.send_message(call.message.chat.id, 'Упс! Что то пошло не так')
        return
    bot.send_message(call.message.chat.id, 'привет')





@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_answer(message):
    category = Category.objects.all()
    bot.send_message(message.chat.id, f'ddd', reply_markup=main_keyboard())


