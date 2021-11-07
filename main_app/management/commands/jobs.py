from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot
import datetime
from main_app.models import *

class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        # while True:
        timenow = datetime.datetime.now(datetime.timezone.utc)
        queryset = PayProduct.objects.all()
        for item in queryset:
            time_passed = abs(int((item.datetime - timenow).total_seconds() / 60))
            if time_passed >= 15:
                item.delete()
                # Сделать возврат удаленных товаров обратно 