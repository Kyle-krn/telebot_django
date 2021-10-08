from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot
import time
from main_app.models import *

class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        text_file = open("sample.log", "a")
        text_file.write("Hi...")
        text_file.write("\n")
        text_file.close()