from django.core.management.base import BaseCommand
from main_app.management.commands.handlers.handlers import bot
import datetime
from main_app.models import *
from django.db.models import Q

class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        # while True:
        timenow = datetime.datetime.now(datetime.timezone.utc)
        queryset = PayProduct.objects.all()
        for item in queryset:
            time_passed = abs(int((item.datetime - timenow).total_seconds() / 60))
            if time_passed >= 2:
                user = item.user
                # cart = TelegramProductCartCounter.objects.filter(Q(user=user) & Q(counter=False))
                # for product_cart in cart:
                #     product_cart.product.count += product_cart.count
                #     product_cart.product.save()
                item.cancel_reservation()
                # Сделать возврат удаленных товаров обратно 