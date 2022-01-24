from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail
from io import BytesIO
import weasyprint
from celery import task
from django.core.mail import send_mail
from .models import OrderSiteProduct
from django.conf import settings

@task
def test_crontab():
    subject = f'Магазин Vape_shop. Заказ #5'
    message = f'Доброго времени суток ! \n\n' \
              f'<! -- ЗДЕСЬ РЕКВИЗИТЫ БАНКОВ ДЛЯ ОПЛАТЫ НА ПРЯМУЮ --!>.\n' \
              f'После оплаты свяжитесь с нашим менеджером и пришлите ему скриншот оплаты .\n' \
              f'<! -- ЗДЕСЬ ВСЕ КОНТАКТЫ НАШЕГО МЕНЕДЕЖРА --!>\n\n'  \
               'ВНИМАНИЕ! ЭТО НЕ НАСТОЯЩИЙ МАГАЗИН, ПОЖАЛУЙСТА НЕ ОПЛАЧИВАЙТЕ ЗАКАЗЫ, \n'  \
               'САЙТ СУЩЕСТВУЕТ КАК ТЕСТОВЫЙ МАГАЗИН'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, ['egorjkee96@gmail.com'])

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
    if order.status == 'Created':
        email = EmailMessage(
		subject,
		message,
		'santa.mail.little.helper@gmail.com',
		[order.email])
        html = render_to_string('pdf.html', {'order': order})
        out = BytesIO()
        stylesheets = [weasyprint.CSS(settings.STATIC_ROOT + '/css/pdf.css')]
        weasyprint.HTML(string=html).write_pdf(out,stylesheets=stylesheets)
        email.attach(f'order_{order.id}.pdf',
			out.getvalue(),
			'application/pdf')
        email.send()
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
