from celery import shared_task
from django.core.mail import send_mail
from online_shop.models import OrderSiteProduct
from django.conf import settings
from seller_site.models import OfflineCategory

@shared_task
def order_created(order_id):
    # order = OrderSiteProduct.objects.get(pk=order_id)
    # subject = f'Order nr. {order.id}'
    # message = f'Dear {order.first_name}, \n\n' \
    #           f'Your order was successfully created.\n' \
    #           f'Your order ID is {order.id}.'
    # mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    # return mail_sent
    # send_mail('golova', 'telo', settings.EMAIL_HOST_USER, ['egorjkee96@gmail.com'])

    # print('here')
    OfflineCategory.objects.create(name='Тест селеру', price_for_seller=100)