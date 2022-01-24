import requests
import json
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.core.mail import send_mail
from io import BytesIO
import weasyprint
from django.conf import settings
from .models import OrderSiteProduct


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
   

