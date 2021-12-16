import requests
import json
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import OrderSiteProduct


def send_email_order_method_payment_qiwi(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Заказ номер {order.id}'
    message = f'Дорогой {order.first_name}, \n\n' \
              f'Статус вашего заказа - Ожидает оплаты.\n' \
              f'Ссылка для оплаты - {order.pay_url}' \
              f'Your order ID is {order.id}.'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent

def send_email_order_method_payment_manager(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Заказ номер {order.id}'
    message = f'Дорогой {order.first_name}, \n\n' \
              f'<! -- ЗДЕСЬ РЕКВИЗИТЫ БАНКОВ ДЛЯ ОПЛАТЫ НА ПРЯМУЮ --!>.\n' \
              f'После оплаты свяжитесь с нашим менеджером и пришлите ему скриншот оплаты .\n' \
              f'<! -- ЗДЕСЬ ВСЕ КОНТАКТЫ НАШЕГО МЕНЕДЕЖРА --!>'
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

def send_email_delete_order(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    subject = f'Заказ номер {order.id}'  
    message = f'Dear {order.first_name}, \n\n' \
              f'Ваш заказ был удален в связи истечением срока оплаты или отклонением оплаты.'
    mail_sent = send_mail(subject, message, settings.EMAIL_HOST_USER, [order.email])
    return mail_sent


def send_bill_api_qiwi(order):
    time_bill = datetime.now().astimezone().replace(microsecond=0) + timedelta(hours=1)
    time_bill = time_bill.isoformat()
    
    headers = {
        'Authorization': f'Bearer {settings.QIWI_PRIVATE_KEY}',
        "Content-Type": "application/json",
        "Accept": "application/json"
        }

    params = {'amount': {'value': float(order.price + order.transport_cost), 
                   'currency': 'RUB',
                   },
        'comment': 'Text comment', 
        'expirationDateTime': time_bill, 
        'customer': {}, 
        'customFields': {},
        }
    
    params = json.dumps(params)

    url = f'https://api.qiwi.com/partner/bill/v1/bills/{order.id}'
    
    res = requests.put(url,
                    headers=headers,
                    data=params,
                    )
    return res.json()


def check_bill_api_qiwi(order):
    headers = {
        'Authorization': f'Bearer {settings.QIWI_PRIVATE_KEY}',
        "Content-Type": "application/json",
        "Accept": "application/json"
        }
    url = f'https://api.qiwi.com/partner/bill/v1/bills/{order.id}'
    res = requests.get(url,headers=headers)
    return res.json()



def create_bill_qiwi(order_id):
    order = OrderSiteProduct.objects.get(pk=order_id)
    response = send_bill_api_qiwi(order)
    return response['payUrl']
   

