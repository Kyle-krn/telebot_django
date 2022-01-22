import datetime
from django.core.management.base import BaseCommand
from django.db.models import Q
from main_app.models import *

class Command(BaseCommand):
    help = 'Чистит базу'

    def handle(self, *args, **kwargs):
        # while True:
        timenow = datetime.datetime.now(datetime.timezone.utc)
        queryset = PayProduct.objects.all()
        for item in queryset:
            time_passed = abs(int((item.datetime - timenow).total_seconds() / 60))
            if time_passed >= 2:
                item.cancel_reservation()
