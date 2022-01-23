from django.core.management.base import BaseCommand
from django.conf import settings
from django.db.models import Q
from bot.management.commands.handlers.handlers import bot
from online_shop.utils import check_bill_api_qiwi, send_email_change_status_order, send_email_delete_order
from online_shop.models import OrderSiteProduct

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
                
                text_for_channel = '<b>Заказ через сайт</b>\n'  \
                                   '<b>Заказ оплачен через QIWI</b>\n\n'  \
                                   f'<b>Сумма корзины {order.price} руб.</b>\n\n'  \
                                   f'<b>Сумма доставки {order.transport_cost} руб.</b>\n\n'
                for item in order.soldproduct.all():
                    text_for_channel += f'<b><u>{item.product.title}</u></b> - {item.count} шт.\n'
                text_for_channel += f'\n<b>Номер телефона покупателя - {order.telephone}</b>'
                bot.send_message(chat_id=settings.TELEGRAM_GROUP_ID, text=text_for_channel, parse_mode='HTML')

            elif res['status']['value'] == 'EXPIRED' or res['status']['value'] == 'REJECTED':
                send_email_delete_order(order.id)
                order.delete()