from .models import OrderSiteProduct
from django.core.mail import send_mail
from django.conf import settings


def send_email_created_order(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Заказ номер {order.id}'
    message = f'Dear {order.first_name}, \n\n' \
              f'Your order was successfully created.\n' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent


def send_email_change_status_order(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Заказ номер {order.id}'  
    message = f'Dear {order.first_name}, \n\n' \
              f'Status of your order {order.id} was changed to {order.status}. \n'
    if order.track_code:
        message +=  f'Track code is {order.track_code}.'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent