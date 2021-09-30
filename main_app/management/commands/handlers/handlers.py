import telebot

TELEGRAM_TOKEN = '2049844837:AAH-f33he41frWIkFqfV78t5f445DhtUHNk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def get_answer(message):
    bot.send_message(message.chat.id, 'Код может состоять только из цифр!')