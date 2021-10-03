import telebot
from main_app.models import *
from .handlers import bot
from django.db.models import Q


@bot.message_handler(regexp='^(Корзина)$')
def cart_handlers(message):
    user = TelegramUser.objects.get(chat_id=message.chat.id)
    cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
    print(cart)