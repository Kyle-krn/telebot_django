from .handlers import bot
from main_app.models import *
from main_app.management.commands.keyboards import *
from vape_shop.settings import DADATA_TOKEN
from dadata import Dadata


@bot.message_handler(regexp='^(Мои товары)$')
def my_purchase(message):
    sold_product = SoldProduct.objects.filter(user__chat_id=message.chat.id)
    if not sold_product:
        text = 'У вас еще нет покупок'
        return bot.send_message(chat_id=message.chat.id, text=text)
