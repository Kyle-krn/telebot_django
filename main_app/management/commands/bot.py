from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot
import logging
import telebot


class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        logger = telebot.logger
        logging.basicConfig(level=logging.INFO, filename='myapp.log', format='%(asctime)s %(levelname)s:%(message)s')
        bot.polling(none_stop=True)