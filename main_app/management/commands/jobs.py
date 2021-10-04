from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot
import time
from main_app.models import *

class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        while True:
            print('hi')
            time.sleep(10)