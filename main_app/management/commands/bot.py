from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot



class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        bot.polling(none_stop=True)