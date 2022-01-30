# import weasyprint
# from io import BytesIO
from celery import task
from django.template.loader import render_to_string
from django.core.mail import send_mail, EmailMessage
from django.db.models import Q
from django.conf import settings
# from bot.management.commands.handlers.handlers import bot
from .models import OrderSiteProduct
from .utils import check_bill_api_qiwi


@task
def send_email_order_method_payment_manager(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Магазин Vape_shop. Заказ #{order_id}'
    message = f'Доброго времени суток {order.first_name}! \n\n' \
              f'<! -- ЗДЕСЬ РЕКВИЗИТЫ БАНКОВ ДЛЯ ОПЛАТЫ НА ПРЯМУЮ --!>.\n' \
              f'После оплаты свяжитесь с нашим менеджером и пришлите ему скриншот оплаты .\n' \
              f'<! -- ЗДЕСЬ ВСЕ КОНТАКТЫ НАШЕГО МЕНЕДЕЖРА --!>\n\n'  \
               'ВНИМАНИЕ! ЭТО НЕ НАСТОЯЩИЙ МАГАЗИН, ПОЖАЛУЙСТА НЕ ОПЛАЧИВАЙТЕ ЗАКАЗЫ, \n'  \
               'САЙТ СУЩЕСТВУЕТ КАК ТЕСТОВЫЙ МАГАЗИН'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent

@task
def send_email_order_method_payment_qiwi(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Магазин Vape_shop. Заказ #{order_id}'
    message = f'Доброго времени суток {order.first_name}! \n\n' \
              f'Статус вашего заказа - Ожидает оплаты.\n' \
              f'Вы можете оплатить заказ по этой ссылке - {order.pay_url}.\n' \
              f'Номер вашего заказа #{order.id}.\n\n'  \
               'ВНИМАНИЕ! ЭТО НЕ НАСТОЯЩИЙ МАГАЗИН, ПОЖАЛУЙСТА НЕ ОПЛАЧИВАЙТЕ ЗАКАЗЫ, \n'  \
               'САЙТ СУЩЕСТВУЕТ КАК ТЕСТОВЫЙ МАГАЗИН'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent

@task
def send_email_change_status_order(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Магазин Vape_shop. Заказ #{order_id}'
    message = f'Доброго времени суток {order.first_name}! \n\n' \
              f'Статус вашего заказа сменился на {order.get_status_display()}. \n'
    if order.track_code:
        message +=  f'Track code is {order.track_code}.'
    # if order.status == 'Created':
    #     email = EmailMessage(
	# 	subject,
	# 	message,
	# 	'santa.mail.little.helper@gmail.com',
	# 	[order.email])
    #     html = render_to_string('pdf.html', {'order': order})
    #     out = BytesIO()
    #     stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')]
    #     weasyprint.HTML(string=html).write_pdf(out,stylesheets=stylesheets)
    #     email.attach(f'order_{order.id}.pdf',
	# 		out.getvalue(),
	# 		'application/pdf')
    #     email.send()
    else:
        mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
        return mail_sent

@task
def send_email_delete_order(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Магазин Vape_shop. Заказ #{order_id}'
    message = f'Доброго времени суток {order.first_name}! \n\n' \
              f'Статус вашего заказа сменился на {order.get_status_display()}. \n'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent


@task
def check_site_qiwi_payment():
    queryset = OrderSiteProduct.objects.filter(Q(status='Awaiting payment') & Q(pay_url__isnull=False))
    for order in queryset:
        res = check_bill_api_qiwi(order)
        if res['status']['value'] == 'PAID':
            order.status = 'Created'
            for item in order.soldproduct.all():
                item.product.count -= item.count
                item.product.save()
            order.save()
            send_email_change_status_order.delay(order.id)
            text_for_channel = '<b>Заказ через сайт</b>\n'  \
                                '<b>Заказ оплачен через QIWI</b>\n\n'  \
                                f'<b>Сумма корзины {order.price} руб.</b>\n\n'  \
                                f'<b>Сумма доставки {order.transport_cost} руб.</b>\n\n'
            for item in order.soldproduct.all():
                text_for_channel += f'<b><u>{item.product.title}</u></b> - {item.count} шт.\n'
            text_for_channel += f'\n<b>Номер телефона покупателя - {order.telephone}</b>'
            # bot.send_message(chat_id=settings.TELEGRAM_GROUP_ID, text=text_for_channel, parse_mode='HTML')

        elif res['status']['value'] == 'EXPIRED' or res['status']['value'] == 'REJECTED':
            send_email_delete_order.delay(order.id)
            order.delete()
