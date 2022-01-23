from django.core.management.base import BaseCommand
from bot.management.commands.handlers.handlers import bot
import logging
import telebot


class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        logger = telebot.logger
        
        telebot.logger.setLevel(logging.INFO)
        bot.polling(none_stop=True)