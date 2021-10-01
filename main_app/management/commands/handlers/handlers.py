import telebot
from main_app.models import *

TELEGRAM_TOKEN = '2049844837:AAH-f33he41frWIkFqfV78t5f445DhtUHNk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_answer(message):
    category = Category.objects.all()[0]
    bot.send_message(message.chat.id, f'{category.name}')