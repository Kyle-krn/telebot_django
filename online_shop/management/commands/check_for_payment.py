from django.core.management.base import BaseCommand
from online_shop.models import OrderSiteProduct
import datetime
import pytz
import time
from django.db.models import Q
from online_shop.utils import check_bill_api_qiwi, send_email_change_status_order, send_email_delete_order

class Command(BaseCommand):
    help = 'Проверяет оплату qiwi'

    def handle(self, *args, **kwargs):
        queryset = OrderSiteProduct.objects.filter(Q(status='Awaiting payment') & Q(pay_url__isnull=False))
        # HERE IS PAID STATUS 
        for order in queryset:
            res = check_bill_api_qiwi(order)
            if res['status']['value'] == 'PAID':
                order.status = 'Created'
                for item in order.soldproduct.all():
                    item.product.count -= item.count
                    item.product.save()
                order.save()
                send_email_change_status_order(order.id)
            elif res['status']['value'] == 'EXPIRED' or res['status']['value'] == 'REJECTED':
                send_email_delete_order(order.id)
                order.delete()