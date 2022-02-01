from django.core.management.base import BaseCommand
from bot.management.commands.handlers.handlers import bot
import logging
import telebot


class Command(BaseCommand):
    help = 'Запускает бота по команде python manage.py bot'

    def handle(self, *args, **kwargs):
        logger = telebot.logger
        
        telebot.logger.setLevel(logging.INFO)
        bot.polling(none_stop=True)
